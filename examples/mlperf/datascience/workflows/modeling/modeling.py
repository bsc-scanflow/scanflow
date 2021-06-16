import tensorflow as tf
import mlflow
import click
import os
import logging

import sys
sys.path.insert(0, '/scanflow/scanflow')

from scanflow.client import ScanflowTrackerClient
import mlflow.keras

# Enable auto-logging to MLflow to capture TensorBoard metrics.
mlflow.keras.autolog()

@click.command(help="Modeling")
@click.option("--model_name", default='resnet', type=str)
@click.option("--model_path", default='/workflow/model', type=str)
def modeling(model_name, model_path):
   
    #log
    client = ScanflowTrackerClient(verbose=True)
    mlflow.set_tracking_uri(client.get_tracker_uri(True))
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        
    mlflow.set_experiment("modeling")
    with mlflow.start_run():
        model = tf.keras.applications.resnet50.ResNet50(
            weights='imagenet'
        )
        #tf.saved_model.load(f"{model_path}")
        tf.saved_model.save(model, "/workflow/model/1")
        mlflow.keras.log_model(model, artifact_path=model_name, 
                          registered_model_name=model_name)

        mlflow.log_artifacts(model_path, artifact_path=f"{model_name}/model/0")


if __name__ == '__main__':
    modeling()