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
# from main scanflow
@click.option("--app_name", default=None, type=str)
@click.option("--team_name", default=None, type=str)
# from local scanflow
@click.option("--experiment_name", default=None, type=str)
@click.option("--run_name", default=None, type=str)
@click.option("--path", default=None, type=str)
@click.option("--run_id", default=None, type=str)
@click.option("--fromlocal", default=False, type=bool)
def loaddata(app_name, team_name, experiment_name, run_name, path, run_id, fromlocal):

    client = ScanflowTrackerClient()
    
    if app_name is not None and team_name is not None:
        #load the latest mnist data from remote tracker
        #data will be download into shared /workflow folder
        artifacts_dir = client.download_app_artifacts(
                                  app_name = app_name, 
                                  team_name = team_name,
                                  local_dir = "/workflow/load-data",
                                  fromlocal=False) 

    if path is not None:
        artifacts_dir = client.download_artifacts(
                                  path = path,
                                  experiment_name = experiment_name,
                                  run_name=run_name,
                                  run_id=run_id,
                                  local_dir="/workflow/load-data",
                                  fromlocal=fromlocal)
    
    #log
    try:
        mlflow.set_tracking_uri(client.get_tracker_uri(True))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

        mlflow.set_experiment("load_data")
        with mlflow.start_run():
            mlflow.log_artifacts(local_dir= artifacts_dir,
                                 artifact_path= "data")
    except:
        logging.info("mlflow logging fail")

    
if __name__ == '__main__':
    loaddata()