import mlflow
from mlflow.tracking import MlflowClient
import click
import logging
import pandas as pd
import os

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

@click.command(help="load input data set")
# from main scanflow
@click.option("--app_name", default=None, type=str)
@click.option("--team_name", default=None, type=str)
# from local scanflow
@click.option("--model_name", default=None, type=str)
@click.option("--model_version", default=None, type=int)
def download(app_name, team_name, model_name, model_version):

    client = ScanflowTrackerClient()
    mlflowclient = MlflowClient(client.get_tracker_uri(False))

    if model_version is not None:
        mv = mlflowclient.get_model_version(model_name, model_version)
    else:
        mv = mlflowclient.get_latest_versions(model_name, stages=["Production"])

    if not os.path.exists("/workflow/model"):
        os.makedirs(f"/workflow/model")

    if app_name is not None and team_name is not None:
        artifacts_dir = mlflowclient.download_artifacts(
		                          mv[0].run_id,
                                  path = f"{model_name}/model",
                                  dst_path = "/workflow/model")
    
    logging.info("Artifacts downloaded in: {}".format(artifacts_dir))
    logging.info("Artifacts: {}".format(os.listdir(artifacts_dir)))
    
if __name__ == '__main__':
    download()