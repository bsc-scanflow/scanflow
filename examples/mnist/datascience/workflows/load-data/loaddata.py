# load data from scanflow-mnist repo to datascience env tracker registry
import mlflow
import click
import logging
import pandas as pd
import time
import numpy as np

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

@click.command(help="load input data set")
@click.option("--app_name", default='mnist', type=str)
@click.option("--team_name", default='data', type=str)
def loaddata(app_name, team_name):

    client = ScanflowTrackerClient(verbose=True)

    #load the latest mnist data from remote tracker
    #data will be download into shared /workflow folder
    client.download_app_artifacts(app_name = app_name, 
                                  team_name = team_name,
                                  local_dir = "/workflow/load-data") 
    
    #log
    try:
        mlflow.set_registry_uri(client.get_tracker_uri(True))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

        mlflow.set_experiment("load_data")
        with mlflow.start_run():
            mlflow.log_artifacts(local_dir= f"/workflow/load-data/{app_name}/{team_name}",
                                 artifact_path= "data")
    except:
        logging.info("mlflow logging fail")

    
if __name__ == '__main__':
    loaddata()