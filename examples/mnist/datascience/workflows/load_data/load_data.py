# load data from scanflow-mnist repo to datascience env tracker registry

import mlflow
import click
import logging
import pandas as pd
import time
import numpy as np

from scanflow.client import ScanflowClient

@click.command(help="load input data set")
@click.option("--app_name", default='mnist', type=str)
@click.option("--server_uri", default='', type=str)
@click.option("--server_tracker_uri", default='', type=str)
@click.option("--y_test_path", default='./images', type=str)
def loaddata(x_train_path, y_train_path, x_test_path, y_test_path):

    client = ScanflowClient(server_uri=server_uri,
                        server_tracker_uri=server_tracker_uri,
                        verbose=True)

    #load the latest data
    client.download_app(app_name, "data", app_dir)

    
    with mlflow.start_run(run_name='loaddata') as mlrun:

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
    loaddata()