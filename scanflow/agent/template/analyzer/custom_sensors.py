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
from functools import reduce

from scanflow.agent.sensors.sensor import sensor
from scanflow.agent.sensors.sensor_dependency import sensor_dependency

from scanflow.client import ScanflowTrackerClient
import mlflow
from mlflow.tracking import MlflowClient
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(True))

custom_sensor_router = APIRouter()

@custom_sensor_router.post("/analyze_check_predictions",
                            status_code= status.HTTP_200_OK)
async def sensors_analyze_predictions(info: tuple = Depends(sensor_dependency)):
    run = info[0]
    print("Active run_id: {}".format(run.info.run_id))
    with mlflow.start_run(run_id=run.info.run_id):

        #logic
        images = []
        labels = []
        mlflowClient = MlflowClient(client.get_tracker_uri(True))
        for run_id in info[2]['run_ids']:
            mlflowClient.download_artifacts(run_id, path="data", dst_path="/tmp")
            images.append(np.load("/tmp/data/images.npy"))
            labels.append(np.load("/tmp/data/labels.npy"))
            
        x_inference = []
        x_inference = np.concatenate((images), axis=0)
        y_inference = []
        y_inference = np.concatenate((labels), axis=0)

        with open('x_inference.npy', 'wb') as f:
            np.save(f, x_inference)
        with open('y_inference.npy', 'wb') as f:
            np.save(f, y_inference)
            
        mlflow.log_artifact('x_inference.npy',artifact_path="data")
        mlflow.log_artifact('y_inference.npy', artifact_path="data") 

    await call_run_analyze_workflow(run_id = run.info.run_id, artifact_path="data")

    return {"detail": "sensors_analyze_predictions received"}


@sensor(executors=["pick-data"], filter_string="metrics.n_critical_data > 0")
async def count_number_of_newdata(runs: List[mlflow.entities.Run], args, kwargs):
    print(args)
    print(kwargs)

    n_newdata = list(map(lambda run: run.data.metrics['n_critical_data'], runs))
    number_of_newdata = reduce(lambda x,y : x+y, n_newdata)
    logging.info(f"count_number_of_newdata - {number_of_newdata}")

    if number_of_newdata_threshold(number_of_newdata):
           await call_plan_retrain_model(run_ids = list(map(lambda run: run.info.run_id, runs)))

    return number_of_newdata

