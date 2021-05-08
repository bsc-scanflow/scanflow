from fastapi import FastAPI, APIRouter

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

custom_sensor_router = APIRouter()

@custom_sensor_router.get("/online")
async def track_new_data_sensor():
    return {"Hello": "custom monitor sensors online"}

def sensor_root():
    return {"Hello": "custom monitor sensors"}

from datetime import datetime
import time

def tock():
    print('Tock! The time is: %s' %  time.strftime("'%Y-%m-%d %H:%M:%S'"))