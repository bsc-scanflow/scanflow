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
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
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

    tracker_uri = "http://localhost:8010/tracker/current/model"
    planner_uri = "http://localhost:8013/planner/plans"
    n_anomalies = feedback['n_anomalies']

    if n_anomalies <= 2:
        response = {'conclusions': f'Normal behavior!, {n_anomalies} anomalies'}
    elif 2 < n_anomalies < 5:
        response = {'conclusions': f'Alert!, {n_anomalies} anomalies'}
    else:
        message = Message("", "INFORM", tracker_uri)

        async with app.aiohttp_session.get(message.receiver) as response:
            result_tracker = await response.json()

        content = {'conclusions': result_tracker['model']}
        message = Message(content, "INFORM", planner_uri)

        async with app.aiohttp_session.post(message.receiver, json=content) as response:
            result_planner = await response.json()

        response = {'conclusions': {
                    "msg": f"Retraining the model!, {n_anomalies} anomalies",
                    "current_model": result_tracker['model'],
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
