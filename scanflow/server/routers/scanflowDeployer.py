from fastapi import APIRouter
from fastapi import FastAPI, Response, status, HTTPException

from ..schemas.app import Application

router = APIRouter()


import sys
import os
sys.path.insert(0,'../../..')

#scanflow
import mlflow
from scanflow.client import ScanflowTrackerClient

from scanflow.deployer.deployer import Deployer
#from scanflow.deployer.argoDeployer import ArgoDeployer
#from scanflow.deployer.volcanoDeployer import VolcanoDeployer
#from scanflow.deployer.seldonDeployer import SeldonDeployer



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