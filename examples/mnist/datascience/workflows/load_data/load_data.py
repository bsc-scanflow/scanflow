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

    #load the latest mnist data from remote tracker
    #data will be download into shared /workflow folder
    client.download_artifacts(app_name = app_name, 
                              team_name = team_name,
                              local_dir = "/workflow/data") 
    
    #log
    client.save_artifacts(app_name = "load_data", 
                          team_name = team_name,
                          tolocal = True)
    
if __name__ == '__main__':
    loaddata()