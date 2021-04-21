import mlflow
from mlflow.tracking import MlflowClient
import logging
import os

from scanflow.tracker.tracker import Tracker
from scanflow.tracker.utils import (
    get_tracker_uri,
)

class MlflowTracker(Tracker):

    def __init__(self,
                 scanflow_tracker_uri=None,
                 scanflow_tracker_local_uri=None,
                 verbose=True):
        super(MlflowTracker, self).__init__(scanflow_tracker_uri,scanflow_tracker_local_uri,verbose)


    def save_app(self, app_name=None, team_name=None, app_dir=None, tolocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(tolocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        self.client = MlflowClient()
        mlflow.set_experiment(app_name)
        with mlflow.start_run(run_name=team_name):
            # Fetch the artifact uri root directory
            artifact_uri = mlflow.get_artifact_uri()
            logging.info("save app in {} to artifact uri: {}".format(app_dir,artifact_uri))
            mlflow.log_artifacts(app_dir, 
                   artifact_path=f"{app_name}/{team_name}")

    def download_app(self, app_name=None, run_id=None, team_name=None, local_dir="/tmp", fromlocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(fromlocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        self.client = MlflowClient()
        if run_id is not None:
            logging.info(f"[download_app] by 'run_id'. {run_id}")
            self.download_artifacts_by_run_id(run_id,app_name,local_dir)
        else:
            if team_name is not None:
                logging.info(f"[download_app] by 'run_name'. {team_name}. Get the latest submission by {team_name}")
                self.download_artifacts_by_run_name(team_name, app_name, local_dir)
            else:
                logging.info(f"[download_app] by 'app_name'. {team_name}. Get the latest submission by {app_name}")
                self.download_artifacts_by_experiment_name(app_name, local_dir)

    def download_artifacts_by_run_id(self, run_id, app_name, local_dir):
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        local_path = self.client.download_artifacts(run_id, app_name, local_dir)
        logging.info("Artifacts downloaded in: {}".format(local_path))
        logging.info("Artifacts: {}".format(os.listdir(local_path)))
    
    def download_artifacts_by_run_name(self, run_name, app_name, local_dir):
        experiment = mlflow.get_experiment_by_name(app_name)
        if experiment is not None:
            experiment_id = experiment.experiment_id
        else:
            logging.info(f"no app {app_name}") 
        filter_string = f"tag.mlflow.runName = '{run_name}'"
        logging.info(f"search_run by {filter_string}")
        run_id = self.get_latest_run_id([experiment_id], filter_string) 
        self.download_artifacts_by_run_id(run_id, app_name, local_dir)
    
    def download_artifacts_by_experiment_name(self, app_name, local_dir):
        experiment = mlflow.get_experiment_by_name(app_name)
        if experiment is not None:
            experiment_id = experiment.experiment_id
        else:
            logging.info(f"no app {app_name}")
        run_id = self.get_latest_run_id([experiment_id])
        self.download_artifacts_by_run_id(run_id, app_name, local_dir) 
    
    def get_latest_run_id(self, experiment_ids, filter_string='', order_by=None):
        logging.info(f"get latest run within the experiment:{experiment_ids}")
        runs = mlflow.search_runs(experiment_ids,filter_string=filter_string,order_by=order_by, output_format='list')
        logging.info(runs[0].to_dictionary())
        return runs[0].info.run_id
    
    
    
    
                                        
    
    
    
    