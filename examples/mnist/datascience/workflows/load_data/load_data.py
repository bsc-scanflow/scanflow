# load data from scanflow-mnist repo to datascience env tracker registry
import mlflow
import click
import logging
import pandas as pd
import time
import numpy as np

from scanflow.client import ScanflowTrackerClient

@click.command(help="load input data set")
@click.option("--app_name", default='mnist', type=str)
@click.option("--team_name", default='data', type=str)
def loaddata(app_name, team_name):

    client = ScanflowTrackerClient(verbose=True)

    #load the latest mnist data from data team
    client.download_artifacts(app_name = app_name, 
                              team_name = team_name)
    
    with mlflow.start_run(run_name='modeling') as mlrun:

    #save the data to local tracker
    client.save_artifacts(app_name = app_name, 
                          team_name = team_name,
                          tolocal = True)
    
if __name__ == '__main__':
    loaddata()