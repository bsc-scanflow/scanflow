import logging
import os

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool

import requests
import json

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ScanflowTrackerClient:
    def __init__(self,
                 scanflow_tracker_uri=None,
                 scanflow_tracker_local_uri=None,
                 tracker="mlflow",
                 verbose=True):
        """
            scanflow_tracker_uri=http://172.30.0.50:46667
                          =http://scanflow-tracker-service.scanflow-system.svc.cluster.local
            tracker now we only support mlflow as tracker backend
        """
        self.verbose = verbose
        self.scanflow_tracker_uri = scanflow_tracker_uri
        self.scanflow_tracker_local_uri = scanflow_tracker_local_uri
        
        if tracker == "mlflow":
            from scanflow.tracker.mlflowTracker import MlflowTracker
            self.tracker = MlflowTracker(scanflow_tracker_uri, scanflow_tracker_local_uri, verbose)
        else:
            raise ValueError("unknown tracker backend: " + tracker)

    def get_tracker_uri(self, islocal):
        return self.tracker.get_tracker_uri(islocal)

    def save_app_artifacts(self, app_name, team_name, app_dir="/workflow", tolocal=False):
        """
           save local implemented app to scanflow server
        """
        self.tracker.save_app_artifacts(app_name, team_name, app_dir, tolocal)

    def download_app_artifacts(self, app_name, run_id=None, team_name=None, local_dir="/workflow", fromlocal=False):
        """
           download remote app to local app_dir
           app_name: project name (e.g., mnist)
           run_id: specific stored artifact of this project (can get the id from the tracker dashboard)
           team_name: who stored this artifact (e.g., datascienceteam)
           local_dir: local dir to save the project
        """
        self.tracker.download_app_artifacts(app_name, run_id, team_name, local_dir, fromlocal)

    def save_app_model(self, app_name:str, team_name:str, model_name: str, model_type: str):
        """
           save prepared production model from local env to remote scanflow tracker
        """
        self.tracker.save_app_model(app_name, team_name, model_name, model_type)

    def download_app_model(self, app_name, team_name, model_name, model_version):
        """
            download  prepared model from remote scanflow tracker to local env 
        """
        self.tracker.download_app_model(app_name, team_name, model_name,model_version)