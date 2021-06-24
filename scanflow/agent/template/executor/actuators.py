import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

import mlflow
from mlflow.tracking import MlflowClient
from scanflow.client import ScanflowTrackerClient

executor_actuators_router = APIRouter(tags=['executor actuators'])

@executor_actuators_router.get("/",
                            status_code= status.HTTP_200_OK)
async def actuators_root():
    print(f"Hello! executor actuators")
    return {"Hello": "executor actuators"}

#custom
try:
    from scanflow.agent.template.executor import custom_actuators
    executor_actuators_router.include_router(custom_actuators.custom_actuators_router, tags=["custom actuators"])
except:
    logging.info("custom_actuators function does not provide a router.")

async def call_transition_model_version(model_name, model_version):
    trackerClient =  ScanflowTrackerClient(verbose=True)
    client = MlflowClient(trackerClient.get_tracker_uri(True))
    client.transition_model_version_stage(model_name, model_version, "Production",  archive_existing_versions=True)