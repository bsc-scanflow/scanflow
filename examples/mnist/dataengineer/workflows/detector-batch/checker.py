import mlflow
from mlflow.tracking import MlflowClient
import click
import logging
import pandas as pd
import numpy as np
import time
import math
import os

from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

import tensorflow as tf
from scipy.stats import gaussian_kde

RANDOM_STATE_SEED = 42

def scale(x):
    img_rows, img_cols = 28, 28
    # x = df.values
    x = x.reshape(x.shape[0], img_rows, img_cols, 1)
    x = x.astype('float32')
    x /= 255

    return x

def get_loss(model, x, change_score=False):
    
    x_pred = model.predict(x)
    x = x.reshape(x.shape[0], 28, 28)
    x_pred = x_pred.reshape(x_pred.shape[0], 28, 28)
    E = pd.DataFrame()

    sz = len(x)
    reconstruction_cost = np.array([np.linalg.norm(np.subtract(x[i],x_pred[i])) for i in range(0,sz)])
    score_anomaly = (reconstruction_cost - np.min(reconstruction_cost)) / np.max(reconstruction_cost)

    if change_score:
        E['Loss_mae'] = 1 - score_anomaly
    else:
        E['Loss_mae'] = score_anomaly

    return E

def detect_anomalies(model, THRESHOLD_LOW, THRESHOLD_HIGH, x_inference):

    # Get AE loss on inference
    E_inference = get_loss(model, x_inference, change_score=False)

    high =  E_inference['Loss_mae'] > THRESHOLD_HIGH
    low =  E_inference['Loss_mae'] < THRESHOLD_LOW

    # print(high | low)
    E_inference['Anomaly'] = high | low

    n_anomalies = sum(E_inference['Anomaly'])

    return n_anomalies, E_inference

@click.command(help="Detect anomalies")
@click.option("--model_name", default='mnist_detector', type=str)
@click.option("--model_version",  default=None, type=int)
@click.option("--model_stage",  default='Production', type=str)
@click.option("--input_data", default='/workflow/load-data/x_inference.npy', type=str)
def inference(model_name, model_version, model_stage, input_data):

    #data
    img_rows, img_cols = 28, 28
    x_inference = np.load(input_data)
    x_inference = x_inference.reshape(x_inference.shape[0], img_rows, img_cols)

    #client
    client = ScanflowTrackerClient(verbose=True)
    mlflow.set_tracking_uri(client.get_tracker_uri(True))
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
    mlflowClient = MlflowClient(client.get_tracker_uri(True))
 
    #log
    mlflow.set_experiment("detector")
    with mlflow.start_run(run_name='detector-batch'):

        #load model 
        if model_version is not None:
            model = mlflow.keras.load_model(
                model_uri=f"models:/{model_name}/{model_version}"
            )
            print(f"Loading model: {model_name}:{model_version}")
            mv = mlflowClient.get_model_version(model_name, model_version)
            THRESHOLD_LOW = mv.tags['THRESHOLD_LOW']
            THRESHOLD_HIGH = mv.tags['THRESHOLD_HIGH']
        else:
            model = mlflow.keras.load_model(
                model_uri=f"models:/{model_name}/{model_stage}"
            )
            print(f"Loading model: {model_name}:{model_stage}")
            mv = mlflowClient.get_latest_versions(model_name, stages=[model_stage])
            THRESHOLD_LOW = mv[0].tags['THRESHOLD_LOW']
            THRESHOLD_HIGH = mv[0].tags['THRESHOLD_HIGH']
        
        
        n_anomalies, E_inference= detect_anomalies(model, float(THRESHOLD_LOW), float(THRESHOLD_HIGH), x_inference)
        
        if not os.path.exists("/workflow/detector-batch"):
            os.mkdir("/workflow/detector-batch")
        E_inference.to_csv('/workflow/detector-batch/E_inference.csv', index=True)
        
        mlflow.log_metric(key='n_anomalies', value=n_anomalies)
        mlflow.log_artifact('/workflow/detector-batch/E_inference.csv',artifact_path="data")


if __name__ == '__main__':
    inference()