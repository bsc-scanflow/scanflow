from fastapi import FastAPI, APIRouter

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))


def sensor_root():
    return {"Hello": "custom monitor sensors"}
