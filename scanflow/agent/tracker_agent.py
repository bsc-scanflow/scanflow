import uvicorn
import os
import json
import mlflow
from typing import Optional, List

from pydantic import BaseModel, HttpUrl
import aiohttp
import logging

from mlflow.tracking import MlflowClient
from fastapi import FastAPI

client = MlflowClient()

class Config():
    agent_name = 'Tracker'
    tracker_belief_filename = 'summary.json'
    checker_agent_uri = "http://localhost:8011/checker/anomaly"
    improver_agent_uri = "http://localhost:8012/improver/conclusions"

# consider put this into startup fastapi function

experiment = client.get_experiment_by_name(Config.agent_name)

if experiment:
    experiment_id = experiment.experiment_id
    logging.info(f"[Tracker]  '{Config.agent_name}' experiment loaded.")
else:
    experiment_id = client.create_experiment(Config.agent_name)
    logging.info(f"[Tracker]  '{Config.agent_name}' experiment does not exist. Creating a new one.")

app = FastAPI(title='Tracker Agent API',
              description='Actions and Beliefs for the Tracker Agent')

@app.on_event("startup")
async def startup_event():
    app.aiohttp_session = aiohttp.ClientSession()

@app.on_event("shutdown")
async def shutdown_event():
    await app.aiohttp_session.close()

class Feedback():
    url: str
    name: str

class Receiver():
    name: str
    address: str #HttpUrl

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


@app.get("/send/checker/anomaly",
         tags=['Actions'],
         summary="Send input to the anomaly detector")
async def send_to_checker():
    runs_info = client.list_run_infos('0', # Default
                                      order_by=["attribute.start_time DESC"])

    if runs_info:
        last_run_id = runs_info[0].run_id
        input_artifact_path = os.path.join("Input", "input.csv")

        # Get the feedback from Checker
        content = {"run_id":last_run_id, "input": input_artifact_path}
        message = Message(content, "INFORM", Config.checker_agent_uri)
        async with app.aiohttp_session.post(message.receiver, json=message.content) as response:
            result_checker = await response.json()

        # Send the feedback to Improver
        content = result_checker['feedback']
        message = Message(content, "INFORM", Config.improver_agent_uri)
        async with app.aiohttp_session.post(message.receiver, json=message.content) as response:
            result_improver = await response.json()

        response = {'feedback': result_checker['feedback'],
                    'conclusions': result_improver['conclusions']}

        with open(Config.tracker_belief_filename, 'w') as fout:
            json.dump(response, fout)

        with mlflow.start_run(experiment_id=experiment_id,
                              run_name=Config.agent_name) as mlrun:
            mlflow.log_artifact(Config.tracker_belief_filename, 'Summary')
            mlflow.log_param(key='response_time',
                             value=1.2)
    else:
        response = {"Result": 'No input found'}

    return response


@app.get("/send/checker/human",
         tags=['Actions'],
         summary="Send input to a human")
async def send_to_checker():
    runs_info = client.list_run_infos('0', # Default
                                      order_by=["attribute.start_time DESC"])

    if runs_info:
        last_run_id = runs_info[0].run_id
        input_artifact_path = os.path.join("Input", "input.csv")

        content = {"run_id":last_run_id, "input": input_artifact_path}
        message = Message(content, "INFORM", Config.checker_agent_uri)

        async with app.aiohttp_session.post(Config.checker_agent_uri, json=message.content) as response:
            result = await response.json()

        response = result['feedback']

    else:
        response = {"Result": 'No input found'}

    return response

@app.get("/tracker/current/model",
         tags=['Beliefs'],
         summary="Get current deployed model")
async def get_current_model():

    response = {"model": 'Model.1.0'}

    return response
# if __name__ == '__main__':
#     uvicorn.run(app, port=8010, host='0.0.0.0', debug=True)
