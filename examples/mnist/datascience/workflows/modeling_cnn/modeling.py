import mlflow
import click
import logging
import pandas as pd
import time
import predictor_utils
import numpy as np
import torch
import mlflow.pytorch

from mlflow.models.signature import infer_signature
from pathlib import Path

@click.command(help="Gather an input data set")
@click.option("--x_train_path", default='./images', type=str)
@click.option("--y_train_path", default='./images', type=str)
@click.option("--x_test_path", default='./images', type=str)
@click.option("--y_test_path", default='./images', type=str)
def modeling(x_train_path, y_train_path, x_test_path, y_test_path):
    with mlflow.start_run(run_name='modeling') as mlrun:

        img_rows, img_cols = 28, 28
        x_train = np.load(x_train_path)
        y_train = np.load(y_train_path)

        x_test = np.load(x_test_path)
        y_test = np.load(y_test_path)

        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols)
            
        model_mnist = predictor_utils.fit_model(x_train, y_train, model_name='mnist_cnn.pt')
        mnist_score = predictor_utils.evaluate(model_mnist, x_test, y_test)
        predictions = predictor_utils.predict_model(model_mnist, x_test)
        
        signature = infer_signature(x_test, predictions)
        mlflow.pytorch.log_model(model_mnist, artifact_path="mnist_cnn", 
                                 signature=signature, registered_model_name="mnist_cnn")

        mlflow.log_param(key='score', value=round(mnist_score, 2))

        mlflow.log_artifact(x_train_path, 'dataset')
        mlflow.log_artifact(y_train_path, 'dataset')
        mlflow.log_artifact(x_test_path, 'dataset')
        mlflow.log_artifact(y_test_path, 'dataset')

if __name__ == '__main__':
    modeling()
