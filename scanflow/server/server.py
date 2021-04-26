import json
import uvicorn
import logging
import mlflow

from fastapi import FastAPI

import sys
import os
sys.path.insert(0,'../..')

from scanflow.server.message import ResponseMessageBase
from scanflow.server.app import Application

#scanflow

from scanflow.client import ScanflowTrackerClient

#from scanflow.deployer.deployer import Deployer
#from scanflow.deployer.argoDeployer import ArgoDeployer
#from scanflow.deployer.volcanoDeployer import VolcanoDeployer
#from scanflow.deployer.seldonDeployer import SeldonDeployer

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


app = FastAPI(title='Scanflow API',
              description='Scanflow Server.',
              )


## scanflow app

@app.post("/submit/scanflowApplication",
          response_model = ResponseMessageBase, 
          tags = ['ScanflowApplication'],
          summary = "Save scanflow application metadata")
async def save_scanflowApplication(app: Application):
    """
      app: scanflowapplication json 
    """
    logging.info(f"call save_scanflowApplication {app.dict()} ")
    client = ScanflowTrackerClient(verbose=True)
    try:
        mlflow.set_tracking_uri(client.get_tracker_uri(False))
        logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        mlflow.set_experiment(app.app_name)
        with mlflow.start_run(run_name=f"scanflow-{app.team_name}"):
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

## scanflow app environment
#@app.post("/create_environment",
#           tags=['Environment'],
#           summary="create environment for scanflow app")
#async def create_environment(app_name, team_name):
#    deployer = Deployer()
#    result = deployer.create_environment(app)
#    return {"success": result}
#
#@app.post("/clean_environment",
#           tags=['Environment'],
#           summary="clean environment for scanflow app")
#async def clean_environment(app_name, team_name):
#
#    return {}
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