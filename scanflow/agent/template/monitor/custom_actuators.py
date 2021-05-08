from fastapi import FastAPI, APIRouter

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

custom_sensor_router = APIRouter()

def sensor_root():
    return {"Hello": "custom monitor sensors"}

@custom_sensor_router.get("/")
def track_new_data_sensor():
    return {"Hello": "custom monitor sensors online"}