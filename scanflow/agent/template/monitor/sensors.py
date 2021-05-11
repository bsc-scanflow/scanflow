#general
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))


monitor_sensors_router = APIRouter(tags=['monitor sensors'])

@monitor_sensors_router.get("/",
                            status_code= status.HTTP_200_OK)
async def sensors_root():
    print(f"Hello! monitor sensors")
    return {"Hello": "monitor sensors"}


#custom
from scanflow.agent.template.monitor import custom_sensors
try:
    monitor_sensors_router.include_router(custom_sensors.custom_sensor_router, tags=["custom sensors"])
except:
    logging.info("custom_sensors function does not provide a router.")



#scanflow monitor sensor
from scanflow.agent.template.monitor.rules import rule_number_of_pictures

#example 1: count number of pictures in last 1 hour 
@monitor_sensors_router.get("/count_number_of_pictures",
                            status_code= status.HTTP_200_OK)
def count_number_of_pictures(executor:str):
    print(executor)
    rule_number_of_pictures(21)
