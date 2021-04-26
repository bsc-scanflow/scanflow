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

@click.command(help="Train a detector")
@click.option("--name", default='mnist_detector', type=str)
@click.option("--x_train_path", default='./images', type=str)
def checker(name, x_train_path):
    with mlflow.start_run(run_name='detector-training') as mlrun:

        img_rows, img_cols = 28, 28
        x_train = np.load(x_train_path)
        
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols)
        
        # ddae_history contains some metrics
        detector, ddae_history = checker_utils.train(x_train, 
                                                    epochs=3, 
                                                    batch_size=128,
                                                    model_path='detector.hdf5')
        
        # Later we will support saving on Model Registry, similar as Training step
#         mlflow.tensorflow.log_model(detector, artifact_path=name, 
#                                    registered_model_name=name)
        
        x_train_path = 'x_train.npy'
        with open(x_train_path, 'wb') as f:
            np.save(f, x_train)        
 
#         mlflow.log_artifact(ddae_history.history['val_loss'])
        mlflow.log_artifact(x_train_path)


if __name__ == '__main__':
    checker()