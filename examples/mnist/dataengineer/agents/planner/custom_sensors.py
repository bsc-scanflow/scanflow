from .custom_rules import *
from .custom_actuators import *
import numpy as np
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
from mlflow.tracking import MlflowClient
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(True))

custom_sensor_router = APIRouter()

@custom_sensor_router.post("/plan_retain_model",
                            status_code= status.HTTP_200_OK)
async def sensors_plan_retain_model(info: tuple = Depends(sensor_dependency)):
    run = info[0]
    print("Active run_id: {}".format(run.info.run_id))
    with mlflow.start_run(run_id=run.info.run_id):

        #logic
        images = []
        labels = []
        mlflowClient = MlflowClient(client.get_tracker_uri(True))
        for run_id in info[2]['run_ids']:
            mlflowClient.download_artifacts(run_id, path="data", dst_path="/tmp")
            images.append(np.load("/tmp/data/x_inference_chosen.npy"))
            labels.append(np.load("/tmp/data/y_inference_chosen.npy"))
            
        x_newdata = []
        x_newdata = np.concatenate((images), axis=0)
        y_newdata = []
        y_newdata = np.concatenate((labels), axis=0)

        with open('x_newdata.npy', 'wb') as f:
            np.save(f, x_newdata)
        with open('y_newdata.npy', 'wb') as f:
            np.save(f, y_newdata)
            
        mlflow.log_artifact('x_newdata.npy', artifact_path="data")
        mlflow.log_artifact('y_newdata.npy', artifact_path="data") 

    await call_run_retrain_workflow(run_id = run.info.run_id, artifact_path="data")

    return {"detail": "sensors_plan_retain_model received"}


@sensor(executors=["modeling_cnn1","modeling_cnn2","mnist"], filter_string="metrics.accuracy > 0", order_by=["metric.accuracy DESC"], max_results=1)
async def check_model_accuracy(runs: List[mlflow.entities.Run], args, kwargs):
    print(args)
    print(kwargs)

    if better_model(runs[0]):
        await call_executor_transit_model(run_id = runs[0].info.run_id)
        #await call_update_workflow(run_id = runs[0].info.run_id, artifact_path="data")

    return f"new model run {runs[0].info.run_id}"

