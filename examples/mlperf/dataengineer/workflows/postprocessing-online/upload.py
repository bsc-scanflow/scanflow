import mlflow
import click
import logging
import pandas as pd
import os
logger = logging.getLogger(__name__)

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

class upload(object):

    def __init__(self, output=None, input=None, preprocess=None):
        print("Init upload")
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
    
    def predict(self, X):
        return X
        
    