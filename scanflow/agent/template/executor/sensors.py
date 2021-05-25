#general
from .rules import *
from .actuators import *
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


#fastapi
from fastapi import FastAPI, APIRouter, Depends
from fastapi import Response, status, HTTPException

from scanflow.agent.sensors.sensor_dependency import sensor_dependency

import mlflow
from mlflow.tracking import MlflowClient
from scanflow.client import ScanflowTrackerClient

executor_sensors_router = APIRouter(tags=['executor sensors'])

#custom
try:
    from scanflow.agent.template.executor import custom_sensors
    executor_sensors_router.include_router(custom_sensors.custom_sensor_router, tags=["custom sensors"])
except:
    logging.info("custom_sensors function does not provide a router.")


@executor_sensors_router.get("/",
                            status_code= status.HTTP_200_OK)
async def sensors_root():
    print(f"Hello! executor sensors")
    return {"Hello": "executor sensors"}

@executor_sensors_router.post("/executor_transit_model",
                            status_code= status.HTTP_200_OK)
async def sensors_executor_transit_model(info: tuple = Depends(sensor_dependency)):
    trackerClient =  ScanflowTrackerClient(verbose=True)
    client = MlflowClient(trackerClient.get_tracker_uri(True))

    run_id = info[2]['run_id']
    filter_string = "run_id='{}'".format(run_id)
    mv = client.search_model_versions(filter_string)
           
    await call_transition_model_version(mv[0].name, mv[0].version)

    return {"detail": "sensors_executor_transit_model received"}