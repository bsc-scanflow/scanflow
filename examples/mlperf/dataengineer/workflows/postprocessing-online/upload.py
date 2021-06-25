import mlflow
import click
import logging
import pandas as pd
import os
import tensorflow as tf
logger = logging.getLogger(__name__)

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

class upload(object):

    def __init__(self, 
                 mlflow_log=None):
        print("Init upload")
        self.mlflow_log = mlflow_log
        client = ScanflowTrackerClient()

        #log
        mlflow.set_tracking_uri(client.get_tracker_uri(True))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

        mlflow.set_experiment("predictor")
        with mlflow.start_run() as run:
            self.run_id = run.info.run_id

        self.epoch = 1
    
    def predict(self, X , names, meta):
        with mlflow.start_run(run_id=self.run_id):
            if self.mlflow_log:
                mlflow.log_metric(key='num_of_predictions',
                value=X.shape[0], step=self.epoch)
                self.epoch = self.epoch + 1
        return X
        
    