import uvicorn
import numpy as np
import os
import mlflow
import json
import pandas as pd
import aiohttp
import logging

from mlflow.tracking import MlflowClient
from mlflow.exceptions import  MlflowException
from typing import Optional, List, Dict

from fastapi import FastAPI, Response, Request, UploadFile
from pydantic import BaseModel, HttpUrl

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


agent_name = 'Improver'
# consider put this into startup fastapi function
client = MlflowClient()

experiment = client.get_experiment_by_name(agent_name)

if experiment:
    experiment_id = experiment.experiment_id
    logging.info(f"[Improver]  '{agent_name}' experiment loaded.")
else:
    experiment_id = client.create_experiment(agent_name)
    logging.info(f"[Improver]  '{agent_name}' experiment does not exist. Creating a new one.")


# except mlflow.exceptions.MlflowException as e:
#     logging.info(f"{e}")
#     logging.info(f"[Improver]  '{agent_name}' experiment does not exist. Creating a new one.", exc_info=True)
#     experiment_id = client.create_experiment(agent_name)

app = FastAPI(title='Improver Agent API',
              description='Actions and Beliefs for the Improver Agent',
              )

@app.on_event("startup")
async def startup_event():
    app.aiohttp_session = aiohttp.ClientSession()

@app.on_event("shutdown")
async def shutdown_event():
    await app.aiohttp_session.close()

class Message(object):
    """
        Abstract Message class.

    """
    def __init__(self,
                 content: dict,
                 performative: str,
                 receiver: str):

        self.content = content
        self.performative = performative
        self.receiver = receiver


@app.post("/improver/conclusions",
          tags=['Actions'],
          summary="Call improver to get conclusions")
async def execute_improver(feedback: dict):
    """
    Call improver to analyze the checker's feedback.
    This agent contains some user-defined rules to take decisions

    - **performative**: Performative action (INFORM, REQUEST, CFP)
    - **content**: Client requests.
    """

    tracker_uri = "http://tracker-agent-mnist:8003/tracker/current/model"
    checker_uri = "http://checker-agent-mnist:8005/feedback/anomaly/last"
    planner_uri = "http://planner-agent-mnist:8007/planner/plans"
    n_anomalies = feedback['n_anomalies']
    p_anomalies = feedback['percentage_anomalies']

    if p_anomalies <= 0.05:
        response = {'conclusions': f'Normal behavior!, {p_anomalies}% anomalies'}
    elif 0.05 < p_anomalies < 0.1:
        response = {'conclusions': f'Alert!, {p_anomalies}% anomalies'}
    else:
        # Get the current model from tracker
        message = Message("", "INFORM", tracker_uri)
        async with app.aiohttp_session.get(message.receiver) as response:
            result_tracker = await response.json(content_type=None)

        
        # Get the input data from checker
        message = Message("", "INFORM", checker_uri)
        async with app.aiohttp_session.get(message.receiver) as response:
            result_checker = await response.json(content_type=None)
        feedback = result_checker['feedback']
        client.download_artifacts(feedback['input_run_id'],
                              feedback['input_path'],
                              '/tmp/')

        input_local_path = os.path.join('/tmp', feedback['input_path'])
        
        # The retraining begins here
        new_model_name = f"{result_tracker['model']['name']}_new"
        print(new_model_name)
        class AddN(mlflow.pyfunc.PythonModel):

            def __init__(self, n):
                self.n = n

            def predict(self, context, model_input):
                return model_input.apply(lambda column: column + self.n)
            
        new_model = AddN(n=5)
        with mlflow.start_run(experiment_id=experiment_id,
                              run_name=agent_name) as mlrun:    
            mlflow.pyfunc.log_model(
                python_model=new_model,
                artifact_path=new_model_name,
                registered_model_name=new_model_name
            )
        # The retraining ends here

        # Communicate with the Planner
        content = {'conclusions': {
                        'order': 'Transition new model to Production.',
                        'current_model_name': result_tracker['model']['name'],
                        'current_model_version': result_tracker['model']['version'],
                        'new_model_name': new_model_name,
                    }
                  }
        message = Message(content, "INFORM", planner_uri)
        async with app.aiohttp_session.post(message.receiver, json=content) as response:
            result_planner = await response.json(content_type=None)

#         print(f"from planner xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx{result_planner}")
        
        response = {'conclusions': {
                        "action": f'Retraining the model using the new data: {input_local_path}',
                        "planner": result_planner,
                    }
                  }

    improver_filename = 'conclusions.json'
    with open(improver_filename, 'w') as fout:
        json.dump(response, fout)

    with mlflow.start_run(experiment_id=experiment_id,
                          run_name=agent_name) as mlrun:
        mlflow.log_artifact(improver_filename, 'Conclusions')

    return  response

@app.get("/improver/conclusions/last",
         tags=['Beliefs'],
         summary='Get last Improver conclusions')
async def get_last_conclusions():
    runs_info = client.list_run_infos(experiment_id,
                                      order_by=["attribute.start_time DESC"])
    if runs_info:
        last_run_id = runs_info[0].run_id
        conclusions_artifact_path = os.path.join('Conclusions', 'conclusions.json')

        try:
            client.download_artifacts(last_run_id,
                                      conclusions_artifact_path,
                                      '/tmp/')
        except:
            response = {"feedback": 'No conclusions found yet'}
            return response

        conclusions_local_path = os.path.join('/tmp', conclusions_artifact_path)
        with open(conclusions_local_path) as fread:
            conclusions = json.load(fread)

        response = {"conclusions": conclusions}
    else:
        response = {"conclusions": 'No experiments yet'}

    return response


# if __name__ == '__main__':
#      uvicorn.run(app, port=8011,
#                  host='0.0.0.0', debug=True)
