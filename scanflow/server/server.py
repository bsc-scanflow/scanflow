import json
import uvicorn
import logging
import mlflow
from typing import Optional

from fastapi import FastAPI

import sys
import os
sys.path.insert(0,'../..')

from scanflow.server.message import ResponseMessageBase
from scanflow.server.app import Application
from scanflow.server.deploy_env import ScanflowEnvironment

#scanflow

from scanflow.client import ScanflowTrackerClient

from scanflow.deployer.deployer import Deployer
#from scanflow.deployer.argoDeployer import ArgoDeployer
#from scanflow.deployer.volcanoDeployer import VolcanoDeployer
#from scanflow.deployer.seldonDeployer import SeldonDeployer

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


app = FastAPI(title='Scanflow API',
              description='Scanflow Server.',
              )

client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))
logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))



@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass



## scanflow app meta
## save/load/update scanflow application
@app.post("/submit/scanflowApplication",
          response_model = ResponseMessageBase, 
          tags = ['ScanflowApplication'],
          summary = "Save scanflow application metadata")
async def save_scanflowApplication(app: Application):
    """
      app: scanflowapplication json 
    """
    logging.info(f"call save_scanflowApplication {app.dict()} ")
    
    try:
        mlflow.set_experiment(app.app_name)
        with mlflow.start_run(run_name=f"scanflow-app-{app.team_name}"):
            artifact_uri = mlflow.get_artifact_uri()
            logging.info("save app to artifact uri: {}".format(artifact_uri))
            mlflow.log_dict(app.dict(), "{}/{}.json".format(app.team_name, app.app_name))
            if app.workflows is not None:
                for workflow in app.workflows:
                    mlflow.log_dict(workflow.dict(), "{}/workflows/{}.json".format(app.team_name, workflow.name))
            if app.agents is not None:
                for agent in app.agents:
                    mlflow.log_dict(agent.dict(), "{}/agents/{}.json".format(app.team_name, agent.name))
        return ResponseMessageBase(status=0)
    except:
        return ResponseMessageBase(status=1)

#@app.post("/list/scanflowApplications",
#          tags=['ScanflowApplication'],
#          summary="List all scanflow application")
#async def list_scanflowApplication(app_name, team_name):
#    """
#    """
#    response = ""
#    return response
#



## save/load/update scanflow model
@app.post("/submit/scanflowModel",
          response_model = ResponseMessageBase, 
          tags = ['ScanflowModel'],
          summary = "Save scanflow model")
async def save_scanflowApplication(app: Application):
    """
      app: scanflowapplication json 
    """
    logging.info(f"call save_scanflowApplication {app.dict()} ")
    
    try:
        mlflow.set_experiment(app.app_name)
        with mlflow.start_run(run_name=f"scanflow-app-{app.team_name}"):
            artifact_uri = mlflow.get_artifact_uri()
            logging.info("save app to artifact uri: {}".format(artifact_uri))
            mlflow.log_dict(app.dict(), "{}/{}.json".format(app.team_name, app.app_name))
            if app.workflows is not None:
                for workflow in app.workflows:
                    mlflow.log_dict(workflow.dict(), "{}/workflows/{}.json".format(app.team_name, workflow.name))
            if app.agents is not None:
                for agent in app.agents:
                    mlflow.log_dict(agent.dict(), "{}/agents/{}.json".format(app.team_name, agent.name))
        return ResponseMessageBase(status=0)
    except:
        return ResponseMessageBase(status=1)



# scanflow app environment
#@app.post("/create_environment",
#           response_model = ResponseMessageBase,
#           tags=['Environment'],
#           summary="create environment for scanflow app")
#async def create_environment(app: Application,
#                             scanflowEnv : Optional[ScanflowEnvironment] = None):
#    if scanflowEnv is None:
#        scanflowEnv = ScanflowEnvironment()
#        namespace = f"scanflow-{app.app_name}-{app.team_name}" 
#        scanflowEnv.namespace = namespace
#        scanflowEnv.tracker_config.TRACKER_STORAGE = f"postgresql://scanflow:scanflow123@postgresql-service.postgresql.svc.cluster.local/{namespace}"
#        scanflowEnv.tracker_config.TRACKER_ARTIFACT = f"s3://scanflow/{namespace}"
#        scanflowEnv.client_config.SCANFLOW_TRACKER_LOCAL_URI = f"http://scanflow-tracker.{namespace}.svc.cluster.local"
#
#    deployer = Deployer()
#    result = deployer.create_environment(scanflowEnv.namespace, scanflowEnv.secret, scanflowEnv.tracker_config, scanflowEnv.client_config, app.tracker, app.agents)
#
#    if result:
#        return ResponseMessageBase(status=0)
#    else:
#        return ResponseMessageBase(status=1)
#
#
#@app.post("/clean_environment",
#           response_model = ResponseMessageBase,
#           tags=['Environment'],
#           summary="clean environment for scanflow app")
#async def clean_environment(app: Application):
#    namespace = f"scanflow-{app.app_name}-{app.team_name}"
#    deployer = Deployer()
#    result = deployer.clean_environment(namespace)
#
#    if result:
#        return ResponseMessageBase(status=0)
#    else:
#        return ResponseMessageBase(status=1)
#
#
### scanflow workflow deployer operations
#async def build_workflows():
#    response = ""
#    return response
#
#async def run_workflows():
#    response = ""
#    return response
#
#async def delete_workflows():
#    response = ""
#    return response