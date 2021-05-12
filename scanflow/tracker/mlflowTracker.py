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

    def save_app_meta(self, app):
        pass

    def download_app_meta(self, app_name, team_name):
        pass

    def save_app_model(self, app_name, team_name, model_name, model_type, model_version):
        #TODO:4.30 Now we only support save pytorch,keras model
        # 1.load model from local
        mlflow.set_tracking_uri(get_tracker_uri(True))
        if model_type == "pytorch":
            if model_version:
                pytorch_model = mlflow.pytorch.load_model(f"models:/{model_name}/{model_version}")
            else:
                pytorch_model = mlflow.pytorch.load_model(f"models:/{model_name}/Production")
        elif model_type == "keras":
            if model_version:
                keras_model = mlflow.keras.load_model(f"models:/{model_name}/{model_version}")
            else:
                keras_model = mlflow.keras.load_model(f"models:/{model_name}/Production")
        else:
            logging.info("unsupported model_type {model_type}")

        # 2. log the model to scanflow
        mlflow.set_tracking_uri(get_tracker_uri())
        mlflow.set_experiment(app_name)
        if model_type == "pytorch":
            with mlflow.start_run(run_name=f"scanflow-model-{team_name}"):
                mlflow.pytorch.log_model(pytorch_model, model_name, registered_model_name=model_name)
        if model_type == "keras":
            with mlflow.start_run(run_name=f"scanflow-model-{team_name}"):
                mlflow.keras.log_model(keras_model, model_name, registered_model_name=model_name)
        else:
            logging.info("unsupported model_type {model_type}")

 
    def download_app_model(self, model_name, model_type, model_version):
        #1. load model from scanflow
        mlflow.set_tracking_uri(get_tracker_uri())
        if model_type == "pytorch":
            if model_version:
                pytorch_model = mlflow.pytorch.load_model(f"models:/{model_name}/{model_version}")
            else:
                pytorch_model = mlflow.pytorch.load_model(f"models:/{model_name}/Production")
        elif model_type == "keras":
            if model_version:
                keras_model = mlflow.keras.load_model(f"models:/{model_name}/{model_version}")
            else:
                keras_model = mlflow.keras.load_model(f"models:/{model_name}/Production")
        else:
            logging.info("unsupported model_type {model_type}")

        # 2. log the model to local env
        mlflow.set_tracking_uri(get_tracker_uri(True))
        mlflow.set_experiment("Scanflow")
        if model_type == "pytorch":
            with mlflow.start_run(run_name=f"scanflow-model"):
                mlflow.pytorch.log_model(pytorch_model, model_name, registered_model_name=model_name)
        if model_type == "keras":
            with mlflow.start_run(run_name=f"scanflow-model"):
                mlflow.keras.log_model(keras_model, model_name, registered_model_name=model_name)
        else:
            logging.info("unsupported model_type {model_type}")

    def save_app_artifacts(self, app_name, team_name, app_dir="/worklfow", tolocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(tolocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        mlflow.set_experiment(app_name)
        with mlflow.start_run(run_name=team_name):
            # Fetch the artifact uri root directory
            artifact_uri = mlflow.get_artifact_uri()
            logging.info("save app in {} to artifact uri: {}".format(app_dir,artifact_uri))
            mlflow.log_artifacts(app_dir, 
                   artifact_path=f"{app_name}/{team_name}")

    def download_app_artifacts(self, app_name, run_id=None, team_name=None, local_dir="/workflow", fromlocal=False):
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
        #{'info': {'artifact_uri': 's3://scanflow/1/c9d4785c2dc240bdb59d859d91f4bfa7/artifacts', 'end_time': 1620023637267, 'experiment_id': '1', 'lifecycle_stage': 'active', 'run_id': 'c9d4785c2dc240bdb59d859d91f4bfa7', 'run_uuid': 'c9d4785c2dc240bdb59d859d91f4bfa7', 'start_time': 1620023623985, 'status': 'FINISHED', 'user_id': 'xpliu'}, 'data': {'metrics': {}, 'params': {}, 'tags': {'mlflow.user': 'xpliu', 'mlflow.source.name': '/gpfs/bsc_home/xpliu/anaconda3/lib/python3.8/site-packages/ipykernel_launcher.py', 'mlflow.source.type': 'LOCAL', 'mlflow.runName': 'data'}}}
        return runs[0].info.run_id
    
    
    
    
                                        
    
    
    
    