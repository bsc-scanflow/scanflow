import mlflow
import click
import logging
import pandas as pd
import time
import modeling_utils
import numpy as np
import torch
import mlflow.pytorch

from mlflow.models.signature import infer_signature
from pathlib import Path

import sys
sys.path.insert(0, '/scanflow/scanflow')

from scanflow.client import ScanflowTrackerClient

@click.command(help="Modeling")
@click.option("--model_name", default='mnist_cnn', type=str)
@click.option("--epochs", default='50', type=int)
@click.option("--x_train_path", default='/workflow/load-data/mnist/data/mnist/train_images.npy', type=str)
@click.option("--y_train_path", default='/workflow/load-data/mnist/data/mnist/train_labels.npy', type=str)
@click.option("--x_test_path", default='/workflow/load-data/mnist/data/mnist/test_images.npy', type=str)
@click.option("--y_test_path", default='/workflow/load-data/mnist/data/mnist/test_labels.npy', type=str)
def modeling(model_name, epochs, x_train_path, y_train_path, x_test_path, y_test_path):
    
    
    # data
    img_rows, img_cols = 28, 28
    x_train = np.load(x_train_path)
    y_train = np.load(y_train_path)

    x_test = np.load(x_test_path)
    y_test = np.load(y_test_path)

    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols)
    
    #parameter
    params = {
      'batch_size': 64,
      'test_batch_size': 1000,
      'epochs': epochs,
      'lr': 1.0,
      'gamma': 0.7,
      'seed': 42,
      'log_interval': 100,
      'save_model': True
    }

    #model    
    model_mnist = modeling_utils.fit_model(params, x_train, y_train, model_name=model_name)
    mnist_score = modeling_utils.evaluate(model_mnist, x_test, y_test)
    predictions = modeling_utils.predict_model(model_mnist, x_test)
    signature = infer_signature(x_test, predictions)

    
    #log
    client = ScanflowTrackerClient(verbose=True)
    try:
        mlflow.set_tracking_uri(client.get_tracker_uri(True))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        
        mlflow.set_experiment("modeling_cnn1")
        with mlflow.start_run():
            mlflow.pytorch.log_model(model_mnist, artifact_path=model_name, 
                                 signature=signature, registered_model_name=model_name)
            mlflow.log_param(key='score', value=round(mnist_score, 2))
    except:
        logging.info("mlflow logging fail")


if __name__ == '__main__':
    modeling()
