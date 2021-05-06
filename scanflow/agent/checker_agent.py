import uvicorn
import numpy as np
import os
import mlflow
import json
import pandas as pd
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

some_file_path = "/home/guess/Desktop/scanflow/pictures/usecase.png"

agent_name = 'Checker'
# consider put this into startup fastapi function
client = MlflowClient()

experiment = client.get_experiment_by_name(agent_name)

if experiment:
    experiment_id = experiment.experiment_id
    logging.info(f"[Checker]  '{agent_name}' experiment loaded.")
else:
    experiment_id = client.create_experiment(agent_name)
    logging.info(f"[Checker]  '{agent_name}' experiment does not exist. Creating a new one.")


# except mlflow.exceptions.MlflowException as e:
#     logging.info(f"{e}")
#     logging.info(f"[Checker]  '{agent_name}' experiment does not exist. Creating a new one.", exc_info=True)
#     experiment_id = client.create_experiment(agent_name)

app = FastAPI(title='Checker Agent API',
              description='Actions and Beliefs for the Checker Agent',
              )


class Feedback(BaseModel):
    url: str
    name: str

class Receiver(BaseModel):
    name: str
    address: str #HttpUrl

class Message(BaseModel):
    performative: str
    content: str
    # receiver: Receiver
    # content: List[Feedback] = []

# class Feedback(BaseModel):
#     performative: str
#     # receiver: Receiver
#     content: List[Feedback] = []

class Belief(): # a belief can be true or false
    """
        A belief can be true or false. If a belief
        is true then it becomes knowledge (a real fact).
    """
    date = ""
    content = ""

beliefs = [
    {'id': 1, 'feedback': 'feedback1'},
    {'id': 2, 'feedback': 'feedback2'}
]

def search(feedback_id):
    for b in beliefs:
        if b['id'] == feedback_id:
            return b

def calculate_anomalies(input_data):
    anomalies = np.random.choice([0, 1], size=(len(input_data),), p=[2./3, 1./3])

    return anomalies

@app.post("/checker/anomaly",
          tags=['Actions'],
          summary="Call anomaly detector")
async def execute_checker_anomaly(content: Dict[str, str]):
    """
    Call the anomaly model to detect drift on client requests.
    It should be called by the Tracker agent providing the following info:

    - **performative**: Performative action (INFORM, REQUEST, CFP)
    - **content**: Client requests.
    """

    client.download_artifacts(content['run_id'],
                              content['input'],
                              '/tmp/')

    input_local_path = os.path.join('/tmp', content['input'])

    df_input = pd.read_csv(input_local_path)

    d_anomalies = {"anomalies": calculate_anomalies(df_input)}
    # d_anomalies = {"anomalies": [1, 0, 1, 1, 0]}
    n_anomalies = sum(d_anomalies['anomalies'])
    p_anomalies = sum(d_anomalies['anomalies'])/len(d_anomalies['anomalies'])

    feedback = {
        'n_anomalies': int(n_anomalies),
        'percentage_anomalies': float(p_anomalies)
    }
    feedback_filename = 'feedback_anomaly.json'
    artifact_name = 'Anomaly'

    df_preds = pd.DataFrame(d_anomalies)
    df_preds.to_csv("anomalies.csv", index=False)

    with open(feedback_filename, 'w') as fout:
        json.dump(feedback, fout)

    with mlflow.start_run(experiment_id=experiment_id,
                          run_name=agent_name) as mlrun:
        mlflow.log_artifact('anomalies.csv', 'Anomaly')
        mlflow.log_artifact(feedback_filename, 'Anomaly')
        mlflow.log_param(key='feedback',
                         value=f"{artifact_name}/{feedback_filename}")

    response = {"feedback": feedback}

    return response

@app.post("/checker/human", tags=['Actions'])
async def execute_checker_human(message: Message):
    answer = 'human_feedback'
    response = {"feedback": answer}
    with mlflow.start_run(experiment_id=experiment_id,
                          run_name=agent_name) as mlrun:
        mlflow.log_param(key='feedback',
                         value=answer)

    return response

@app.get("/feedback/anomaly/last",
         tags=['Beliefs'],
         summary='Get last anomaly feedback')
async def get_last_feedback():
    runs_info = client.list_run_infos(experiment_id,
                                      order_by=["attribute.start_time DESC"])
    if runs_info:
        last_run_id = runs_info[0].run_id
        feedback_artifact_path = os.path.join('Anomaly', 'feedback_anomaly.json')

        try:
            client.download_artifacts(last_run_id,
                                      feedback_artifact_path,
                                      '/tmp/')
        except:
            response = {"feedback": 'No anomaly feedback yet'}
            return response

        feedback_local_path = os.path.join('/tmp', feedback_artifact_path)
        with open(feedback_local_path) as fread:
            feedback = json.load(fread)

        response = {"feedback": feedback}
    else:
        response = {"feedback": 'No experiments yet'}

    return response

@app.get("/feedback/human/last",
         tags=['Beliefs'],
         summary='Get last human feedback')
async def get_last_feedback():
    runs_info = client.list_run_infos(experiment_id,
                                      order_by=["attribute.start_time DESC"])
    if runs_info:
        last_run_id = runs_info[0].run_id
        feedback_artifact_path = os.path.join('Human', 'feedback_human.json')

        try:
            client.download_artifacts(last_run_id,
                                      feedback_artifact_path,
                                      '/tmp/')
        except:
            response = {"feedback": 'No human feedback yet'}
            return response

        feedback_local_path = os.path.join('/tmp', feedback_artifact_path)
        with open(feedback_local_path) as fread:
            feedback = json.load(fread)

        response = {"feedback": feedback}
    else:
        response = {"feedback": 'No experiments yet'}

    return response

# @app.get("/feedback/{feedback_id}", tags=['Beliefs'])
# async def get_feedback_by_id(feedback_id: int):
#     response = {"feedback_id": feedback_id,
#                 "feedback": search(feedback_id)}
#     return response

# @app.get("/items/{item_id}")
# def read_root(item_id: str, request: Request):
#     client_host = request.client.host
#     client_port = request.client.port
#     return {"client_host": client_host,
#             "client_port": client_port,
#             "item_id": item_id}

# @app.get("/critical")
# async def main():
#     return Response(some_file_path)
    # return RedirectResponse(url=some_file_path)

# if __name__ == '__main__':
#      uvicorn.run(app, port=8011,
#                  host='0.0.0.0', debug=True)
