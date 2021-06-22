import mlflow
import click
import logging
import pandas as pd
import os

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

@click.command(help="upload predictor")
@click.option("--input", default=None, type=str)
@click.option("--output", default=None, type=str)
@click.option("--preprocess", default=None, type=str)
def upload(input, output, preprocess):

    client = ScanflowTrackerClient()

    #log
    mlflow.set_tracking_uri(client.get_tracker_uri(True))
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

    mlflow.set_experiment("predictor")
    with mlflow.start_run():
        if output:
            mlflow.log_artifacts(local_dir= output,
                                 artifact_path= "output")
        if input:
            mlflow.log_artifacts(local_dir= input,
                                 artifact_path= "input")
        if preprocess:
            mlflow.log_artifacts(local_dir= preprocess,
                                 artifact_path= "preprocess")
    
if __name__ == '__main__':
    upload()