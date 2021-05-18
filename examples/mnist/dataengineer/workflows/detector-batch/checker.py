import mlflow
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

def get_loss(model, x, x_index, change_score=False):
    
    x_pred = model.predict(x)
    x = x.reshape(x.shape[0], 28, 28)
    x_pred = x_pred.reshape(x_pred.shape[0], 28, 28)
    E = pd.DataFrame(index=x_index)

    sz = len(x)
    reconstruction_cost = np.array([np.linalg.norm(np.subtract(x[i],x_pred[i])) for i in range(0,sz)])
    score_anomaly = (reconstruction_cost - np.min(reconstruction_cost)) / np.max(reconstruction_cost)

    if change_score:
        E['Loss_mae'] = 1 - score_anomaly
    else:
        E['Loss_mae'] = score_anomaly

    return E

def decide_threshold(ddae_model, x_train, x_train_index, wanted_anomalies=10):

    width = 0.1
    quantile_high = 0.95
    quantile_low = 1.0 - quantile_high
    # if n_anomalies:
    for trials in range(1, 3): # Iterate until 0.6, 0.4

      # Use default score_anomaly
        E_train = get_loss(ddae_model, x_train, x_train_index, change_score=False)
        # Define threshold
        THRESHOLD_HIGH = E_train['Loss_mae'].quantile(q=quantile_high)
        THRESHOLD_LOW = E_train['Loss_mae'].quantile(q=quantile_low)
        # Get AE loss on test
        E_test = get_loss(ddae_model, x_test, x_test_index, change_score=False)

        high =  E_test['Loss_mae'] > THRESHOLD_HIGH
        low =  E_test['Loss_mae'] < THRESHOLD_LOW

        # print(high | low)
        E_test['Anomaly'] = high | low

        E_full = pd.concat([E_train, E_test], sort=False)
        # E_full['Threshold2'] = NAIVE_THRESHOLD
        E_full['Threshold_high'] = THRESHOLD_HIGH
        E_full['Threshold_low'] = THRESHOLD_LOW

        n_anomalies = sum(E_test['Anomaly'])
        print(f"Anomalies={n_anomalies}|Wanted={wanted_anomalies}")
        if sum(E_test['Anomaly']) >= wanted_anomalies:
        # print(f"Anomalies={n_anomalies}|Wanted={wanted_anomalies}")
            break
        quantile_high = quantile_high - width
        quantile_low = 1.0 - quantile_high

          # print(quantile_high)


    return E_train, E_test, E_full

def get_detector(x_train_, model_name='checker.hdf5', model_stage='Production', date=None, wanted_anomalies=10):
    #np.random.seed(RANDOM_STATE_SEED)
    #tf.random.set_seed(RANDOM_STATE_SEED)

    #data
    x_train_index = None

    if date is not None:
        range_periods = x_train_.shape[0]
        concat_indexes = pd.date_range(date, freq="0.1ms",
                                       periods=range_periods)
        x_train_index = concat_indexes[:x_train_.shape[0]]

    x_train_ = scale(np.copy(x_train_))


    #load model        
    if model_stage:
        model = mlflow.keras.load_model(
            model_uri=f"models:/{model_name}/{model_stage}"
        )
        print(f"Loading model: {model_name}:{model_stage}")


    E_train, E_test, E_full  = decide_threshold(model,
                                                x_train_, x_train_index,
                                                wanted_anomalies)


    x_test_df = pd.DataFrame(x_test_index)

    return ddae_model, E_full, E_test, x_test_df


@click.command(help="Detect anomalies")
@click.option("--model_name", default='mnist-detector', type=str)
@click.option("--model_stage",  default='Production', type=str)
@click.option("--input_data", default='/workflow/load-predicted-data/x_newdata.npy', type=str)
def inference(model_name, model_stage, input_data):
    
    #client
    client = ScanflowTrackerClient(verbose=True)
    mlflow.set_tracking_uri(client.get_tracker_uri(True))
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
 
    #log
    mlflow.set_experiment("detector-batch")
    with mlflow.start_run(run_name='detector-batch'):
        
        img_rows, img_cols = 28, 28
        x_inference = np.load(input_data)
        
        x_inference = x_inference.reshape(x_inference.shape[0], img_rows, img_cols)
        
        date = datetime.today()
        wanted_anomalies = int(x_inference.shape[0]*0.4)
        detector, E_full, E_test, test = get_detector(x_inference, model_path=detector_path,
                            date=date, 
                            wanted_anomalies=wanted_anomalies)
        
        E_full.to_csv("E_full.csv", index=True)
        E_test.to_csv("E_test.csv", index=True)
        
        mlflow.log_metric(key='n_anomalies', value=sum(E_test['Anomaly']))
 
        print(E_test.head())

        mlflow.log_artifact('E_full.csv')
        mlflow.log_artifact('E_test.csv')


if __name__ == '__main__':
    inference()