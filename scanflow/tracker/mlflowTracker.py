import mlflow
from mlflow.tracking import MlflowClient
import logging
import os
import json

from scanflow.tracker.tracker import Tracker
from scanflow.tracker.utils import (
    get_tracker_uri,
)
from scanflow.app import Application, dict_to_app, dict_to_workflow, dict_to_agent, dict_to_executor

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class MlflowTracker(Tracker):

    def __init__(self,
                 scanflow_tracker_uri=None,
                 scanflow_tracker_local_uri=None,
                 verbose=True):
        super(MlflowTracker, self).__init__(scanflow_tracker_uri,scanflow_tracker_local_uri,verbose)

    #tested
    def save_app_meta(self, app: Application, tolocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(tolocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

        mlflow.set_experiment(app.app_name)
        with mlflow.start_run(run_name=f"scanflow-app-{app.team_name}"):
            artifact_uri = mlflow.get_artifact_uri()
            logging.info("save app to artifact uri: {}".format(artifact_uri))
            mlflow.log_dict(app.to_dict(), "{}/{}/{}.json".format(app.app_name, app.team_name, app.app_name))
            if app.workflows is not None:
                for workflow in app.workflows:
                    mlflow.log_dict(workflow.to_dict(), "{}/{}/workflows/{}.json".format(app.app_name, app.team_name, workflow.name))
            if app.agents is not None:
                for agent in app.agents:
                    mlflow.log_dict(agent.to_dict(), "{}/{}/agents/{}.json".format(app.app_name, app.team_name, agent.name))
    
    #tested
    def download_app_meta(self, app_name, team_name, run_id=None, local_dir="/workflow", fromlocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(fromlocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        self.client = MlflowClient()
        if run_id is not None:
            logging.info(f"[download_app_meta] by 'run_id'. {run_id}")
            return self.download_artifacts_by_run_id(run_id, f"{app_name}/{team_name}/{app_name}.json", local_dir)
        else:
            logging.info(f"[download_app_meta] by 'run_name'. {team_name}. Get the latest submission by {team_name}")
            return self.download_artifacts_by_run_name(app_name, f"scanflow-app-{team_name}", f"{app_name}/{team_name}/{app_name}.json", local_dir)
    
    def download_app(self, app_name, team_name, run_id=None, local_dir="/workflow", fromlocal=False):
        app_dir = self.download_app_meta(app_name, team_name, run_id=run_id, local_dir=local_dir, fromlocal=fromlocal)
        with open(app_dir,'r') as load_file:
            app_dict = json.load(load_file)
        logging.info(f"app_dict: {app_dict}")
        return dict_to_app(app_dict)

    #tested
    def download_workflow_meta(self, app_name, team_name, workflow_name, run_id=None, local_dir="/workflow", fromlocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(fromlocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        self.client = MlflowClient()
        if run_id is not None:
            logging.info(f"[download_workflow_meta] by 'run_id'. {run_id}")
            return self.download_artifacts_by_run_id(run_id, f"{app_name}/{team_name}/workflows/{workflow_name}.json", local_dir)
        else:
            logging.info(f"[download_workflow_meta] by 'run_name'. {team_name}. Get the latest submission by {team_name}")
            return self.download_artifacts_by_run_name(app_name, f"scanflow-app-{team_name}", f"{app_name}/{team_name}/workflows/{workflow_name}.json", local_dir)

    def download_workflow(self, app_name, team_name, workflow_name, run_id=None, local_dir="/workflow", fromlocal=False):
        workflow_dir = self.download_workflow_meta(app_name, team_name, workflow_name, run_id=run_id, local_dir=local_dir, fromlocal=fromlocal)
        with open(workflow_dir,'r') as load_file:
            workflow_dict = json.load(load_file)
        logging.info(f"workflow_dict: {workflow_dict}")
        return dict_to_workflow(workflow_dict) 

    def download_agent_meta(self, app_name, team_name, agent_name, run_id=None, local_dir="/workflow", fromlocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(fromlocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        self.client = MlflowClient()
        if run_id is not None:
            logging.info(f"[download_workflow_meta] by 'run_id'. {run_id}")
            return self.download_artifacts_by_run_id(run_id, f"{app_name}/{team_name}/agents/{agent_name}.json", local_dir)
        else:
            logging.info(f"[download_workflow_meta] by 'run_name'. {team_name}. Get the latest submission by {team_name}")
            return self.download_artifacts_by_run_name(app_name, f"scanflow-app-{team_name}", f"{app_name}/{team_name}/agents/{agent_name}.json", local_dir)

    def download_agent(self, app_name, team_name, agent_name, run_id=None, local_dir="/workflow", fromlocal=False):
        agent_dir = self.download_workflow_meta(app_name, team_name, agent_name, run_id=run_id, local_dir=local_dir, fromlocal=fromlocal)
        with open(agent_dir,'r') as load_file:
            agent_dict = json.load(load_file)
        logging.info(f"agent_dict: {agent_dict}")
        return dict_to_agent(agent_dict) 

    #tested
    def save_app_model(self, app_name, team_name, model_name, model_version):
        #load
        mlflow.set_tracking_uri(get_tracker_uri(True))
        client = MlflowClient(get_tracker_uri(True))
        if model_version is not None:
            mv = client.get_model_version(model_name, model_version)
        else:
            mv = client.get_latest_versions(model_name, stages=["Production"])
        if not os.path.exists(f"/tmp/model/{model_name}"):
            os.makedirs(f"/tmp/model/{model_name}")
        local_path = client.download_artifacts(mv.run_id, path=model_name, dst_path=f"/tmp/model/{model_name}")
        #logging.info("Artifacts downloaded in: {}".format(local_path))
        #logging.info("Artifacts: {}".format(os.listdir(local_path)))

        #get run
        run = mlflow.get_run(mv.run_id)
        metrics = run.data.metrics
        params = run.data.params
        logging.info(f"{metrics}--{params}")

        #save
        mlflow.set_tracking_uri(get_tracker_uri(False))
        mlflow.set_experiment(app_name)
        with mlflow.start_run(run_name=f"scanflow-model-{team_name}") as run:
            mlflow.log_metrics(metrics)
            mlflow.log_params(params)
            #model
            mlflow.log_artifacts(f"/tmp/model/{model_name}")
            client = MlflowClient(get_tracker_uri(False))
            try:
                client.create_registered_model(model_name)
            except:
                logging.info(f"{model_name} exists")
            model_uri = "runs:/{}/{}".format(run.info.run_id, model_name)
            mv_new = client.create_model_version(model_name, model_uri, run.info.run_id, mv.tags)
            client.set_registered_model_alias(model_name, "Production", mv_new.version)

    #tested
    def download_app_model(self, model_name, model_version):
        #load
        mlflow.set_tracking_uri(get_tracker_uri(False))
        client = MlflowClient(get_tracker_uri(False))
        if model_version is not None:
            mv = client.get_model_version(model_name, model_version)
        else:
            mv = client.get_latest_versions(model_name, stages=["Production"])
        if not os.path.exists(f"/tmp/model/{model_name}"):
            os.makedirs(f"/tmp/model/{model_name}")
        local_path = client.download_artifacts(mv.run_id, path=model_name, dst_path=f"/tmp/model/{model_name}")
        #logging.info("Artifacts downloaded in: {}".format(local_path))
        #logging.info("Artifacts: {}".format(os.listdir(local_path)))
        
        #get run
        run = mlflow.get_run(mv.run_id)
        run_name = run.data.tags['mlflow.runName']
        experiment = mlflow.get_experiment(run.info.experiment_id)
        experiment_name = experiment.name
        metrics = run.data.metrics
        params = run.data.params
        logging.info(f"{experiment_name}--{run_name}--{metrics}--{params}")

        #save
        mlflow.set_tracking_uri(get_tracker_uri(True))
        mlflow.set_experiment(experiment_name)
        with mlflow.start_run(run_name=run_name) as run:
            mlflow.log_metrics(metrics)
            mlflow.log_params(params)
            #model
            mlflow.log_artifacts(f"/tmp/model/{model_name}")
            client = MlflowClient(get_tracker_uri(True))
            try:
                client.create_registered_model(model_name)
            except:
                logging.info(f"{model_name} exists")
            model_uri = "runs:/{}/{}".format(run.info.run_id, model_name)
            mv_new = client.create_model_version(model_name, model_uri, run.info.run_id, mv.tags)
            #client.transition_model_version_stage(model_name, mv_new.version, "Production",  archive_existing_versions=True)

    #tested
    def save_app_artifacts(self, app_name, team_name, app_dir="/tmp", tolocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(tolocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        mlflow.set_experiment(app_name)
        with mlflow.start_run(run_name=team_name):
            # Fetch the artifact uri root directory
            artifact_uri = mlflow.get_artifact_uri()
            logging.info("save app in {} to artifact uri: {}".format(app_dir,artifact_uri))
            mlflow.log_artifacts(app_dir, 
                   artifact_path=f"{app_name}/{team_name}")

    #tested
    def download_app_artifacts(self, app_name, team_name, run_id=None, local_dir="/tmp", fromlocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(fromlocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        self.client = MlflowClient()
        if run_id is not None:
            logging.info(f"[download_app] by 'run_id'. {run_id}")
            return self.download_artifacts_by_run_id(run_id, f"{app_name}/{team_name}", local_dir)
        else:
            logging.info(f"[download_app] by 'run_name'. {team_name}. Get the latest submission by {team_name}")
            return self.download_artifacts_by_run_name(app_name, team_name, f"{app_name}/{team_name}", local_dir)

    def download_artifacts(self, path, experiment_name=None, run_name=None, run_id=None, local_dir="/workflow", fromlocal=False):
        mlflow.set_tracking_uri(get_tracker_uri(fromlocal))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        self.client = MlflowClient()
        if run_id is not None:
            logging.info(f"[download_artifacts] by 'run_id'. {run_id}")
            return self.download_artifacts_by_run_id(run_id, path, local_dir)
        else:
            logging.info(f"[download_artifacts] by 'run_name'. {run_name}. Get the latest submission by {run_name}")
            return self.download_artifacts_by_run_name(app_name, team_name, path, local_dir)

    def download_artifacts_by_run_id(self, run_id, path, local_dir):
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        local_path = self.client.download_artifacts(run_id, path, local_dir)
        return local_path
        #logging.info("Artifacts downloaded in: {}".format(local_path))
        #logging.info("Artifacts: {}".format(os.listdir(local_path)))
    
    def download_artifacts_by_run_name(self, experiment_name, run_name, path, local_dir):
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is not None:
            experiment_id = experiment.experiment_id
        else:
            logging.info(f"no experiment {experiment_name}") 
        filter_string = f"tag.mlflow.runName = '{run_name}'"
        logging.info(f"search_run by {filter_string}")
        run_id = self.get_latest_run_id([experiment_id], filter_string) 
        return self.download_artifacts_by_run_id(run_id, path, local_dir)
    
#    def download_artifacts_by_experiment_name(self, app_name, local_dir):
#        experiment = mlflow.get_experiment_by_name(app_name)
#        if experiment is not None:
#            experiment_id = experiment.experiment_id
#        else:
#            logging.info(f"no app {app_name}")
#        run_id = self.get_latest_run_id([experiment_id])
#        return self.download_artifacts_by_run_id(run_id, app_name, local_dir) 
    
    def get_latest_run_id(self, experiment_ids, filter_string='', order_by=None):
        logging.info(f"get latest run within the experiment:{experiment_ids}")
        runs = mlflow.search_runs(experiment_ids,filter_string=filter_string,order_by=order_by, output_format='list')
        logging.info(runs[0].to_dictionary())
        #{'info': {'artifact_uri': 's3://scanflow/1/c9d4785c2dc240bdb59d859d91f4bfa7/artifacts', 'end_time': 1620023637267, 'experiment_id': '1', 'lifecycle_stage': 'active', 'run_id': 'c9d4785c2dc240bdb59d859d91f4bfa7', 'run_uuid': 'c9d4785c2dc240bdb59d859d91f4bfa7', 'start_time': 1620023623985, 'status': 'FINISHED', 'user_id': 'xpliu'}, 'data': {'metrics': {}, 'params': {}, 'tags': {'mlflow.user': 'xpliu', 'mlflow.source.name': '/gpfs/bsc_home/xpliu/anaconda3/lib/python3.8/site-packages/ipykernel_launcher.py', 'mlflow.source.type': 'LOCAL', 'mlflow.runName': 'data'}}}
        return runs[0].info.run_id
    
    
    
    
                                        
    
    
    
    