from .custom_rules import *
from .custom_actuators import *
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#fastapi
from fastapi import FastAPI, APIRouter, Depends
from fastapi import Response, status, HTTPException

from datetime import datetime
import time

from scanflow.agent.sensors.sensor import sensor
from scanflow.agent.sensors.sensor_dependency import sensor_dependency

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

custom_sensor_router = APIRouter()

@custom_sensor_router.post("/analyze_predictions",
                            status_code= status.HTTP_200_OK)
async def sensors_analyze_predictions(info: tuple = Depends(sensor_dependency)):
    print(info[0])
    print(info[1])
    print(info[2])


    return {"detail": "analyzed predictions"}


@sensor(executors=["checker"], filter_string="", order_by="")
async def count_number_of_anomalies(run_ids: List[str]):
    print("sensor"+run_ids[0])
    if rule_number_of_predictions(10000):
        await analyze_predictions(run_ids,"a")

