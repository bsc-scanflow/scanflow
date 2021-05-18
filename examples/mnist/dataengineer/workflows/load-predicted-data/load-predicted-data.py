import mlflow
import click
import logging
import pandas as pd
import time
import numpy as np

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

@click.command(help="load predicted data set")
@click.option("--run_id", default='be066cefe8784a248aa3f6e89f70d4f6', type=str)
@click.option("--agent_name", default='checker-agent', type=str)
def loaddata(run_id, agent_name):

    client = ScanflowTrackerClient(verbose=True)
    mlflow.set_tracking_uri(client.get_tracker_uri(True))
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

    #data will be download into shared /workflow folder
    client.download_app_artifacts(app_name = agent_name, 
                                  run_id = run_id,
                                  local_dir = "/workflow/load-predicted-data") 
    
    #log
    try:
        mlflow.set_experiment("load_predicted_data")
        with mlflow.start_run():
            mlflow.log_artifacts(local_dir= f"/workflow/load-predicted-data")
    except:
        logging.info("mlflow logging fail")

    
if __name__ == '__main__':
    loaddata()