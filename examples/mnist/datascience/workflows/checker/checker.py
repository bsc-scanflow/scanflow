import mlflow
import click
import logging
import pandas as pd
import numpy as np
import checker_utils
import numpy as np
import tensorflow as tf
import math
import os

from datetime import datetime
from pathlib import Path

from scanflow.client import ScanflowTrackerClient

@click.command(help="Train a detector")
@click.option("--model_name", default='mnist_detector', type=str)
@click.option("--x_train_path", default='./images', type=str)
def checker(model_name, x_train_path):

    #data
    img_rows, img_cols = 28, 28
    x_train = np.load(x_train_path)
    
    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols)
    
    #modeling
    detector, ddae_history = checker_utils.train(x_train, 
                                                    epochs=3, 
                                                    batch_size=128,
                                                    model_path='detector.hdf5')

    #log
    client = ScanflowTrackerClient(verbose=True)
    try:       
        mlflow.set_tracking_uri(client.get_tracker_uri(True)) 
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

        mlflow.set_experiment("checker")
        with mlflow.start_run():
            mlflow.tensorflow.log_model(detector, artifact_path=model_name, 
                                       registered_model_name=model_name)
            
            mlflow.log_param(key='val_loss', value=ddae_history.history['val_loss'])
    except:
        logging.info("mlflow logging fail")


if __name__ == '__main__':
    checker()