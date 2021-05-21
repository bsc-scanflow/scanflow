from fastapi import APIRouter
from fastapi import FastAPI, Response, status, HTTPException

from ..schemas.app import Application
from ..schemas.deploy_env import ScanflowEnvironment

from typing import Optional

router = APIRouter()

import sys
import os
sys.path.insert(0,'../../..')

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#scanflow
import mlflow
from scanflow.client import ScanflowTrackerClient

from scanflow.deployer.deployer import Deployer
#from scanflow.deployer.argoDeployer import ArgoDeployer
#from scanflow.deployer.volcanoDeployer import VolcanoDeployer
#from scanflow.deployer.seldonDeployer import SeldonDeployer


# scanflow app environment
@router.post("/create_environment",
           summary="create environment for scanflow app",
           status_code = status.HTTP_200_OK)
async def create_environment(app: Application,
                             scanflowEnv : Optional[ScanflowEnvironment] = None):
    logging.info(f"app {app.dict()}")

    if scanflowEnv is None:
        scanflowEnv = ScanflowEnvironment()
        namespace = f"scanflow-{app.app_name}-{app.team_name}" 
        scanflowEnv.namespace = namespace
        scanflowEnv.tracker_config.TRACKER_STORAGE = f"postgresql://scanflow:scanflow123@postgresql-service.postgresql.svc.cluster.local/{namespace}"
        scanflowEnv.tracker_config.TRACKER_ARTIFACT = f"s3://scanflow/{namespace}"
        scanflowEnv.client_config.SCANFLOW_TRACKER_LOCAL_URI = f"http://scanflow-tracker.{namespace}.svc.cluster.local"

    deployer = Deployer()
    result = deployer.create_environment(scanflowEnv.namespace, scanflowEnv.secret.dict(), scanflowEnv.tracker_config.dict(), scanflowEnv.client_config.dict(), app.tracker, app.agents)

    if result:
        return {'detail': "environment created"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="create environment error")


@router.post("/clean_environment",
           summary="clean environment for scanflow app",
           status_code = status.HTTP_200_OK)
async def clean_environment(app: Application):
    logging.info(f"app {app.dict()}")

    namespace = f"scanflow-{app.app_name}-{app.team_name}"
    deployer = Deployer()
    result = deployer.clean_environment(namespace)

    if result:
        return {'detail': "environment cleaned"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="clean environment error")


## scanflow workflow deployer operations
async def build_workflows():
    response = ""
    return response

@router.post("/run_app",
           summary="run all workflows within the application",
           status_code = status.HTTP_200_OK)
async def run_app(app: Application):
    namespace = f"scanflow-{app.app_name}-{app.team_name}"
    deployer = Deployer()
    return response

@router.post("/delete_app",
           summary="delete all workflows within the application",
           status_code = status.HTTP_200_OK)
async def delete_app():
    response = ""
    return response

@router.post("/run_workflows",
           summary="run workflows",
           status_code = status.HTTP_200_OK)
async def run_workflows():
    pass

@router.post("/delete_workflows",
           summary="delete workflows",
           status_code = status.HTTP_200_OK)
async def delete_workflows():
    pass

@router.post("/run_workflow",
           summary="run workflow",
           status_code = status.HTTP_200_OK)
async def run_workflow():
    pass

@router.post("/delete_workflow",
           summary="delete workflow",
           status_code = status.HTTP_200_OK)
async def delete_workflow():
    pass

@router.post("/run_executor",
           summary="run executor",
           status_code = status.HTTP_200_OK)
async def run_executor():
    pass

@router.post("/delete_executor",
           summary="delete executor",
           status_code = status.HTTP_200_OK)
async def delete_executor():
    pass



def get_deployer(deployer):
    if deployer == "argo":
        from scanflow.deployer.argoDeployer import ArgoDeployer
        return ArgoDeployer()
    elif deployer == "volcano":
        from scanflow.deployer.volcanoDeployer import VolcanoDeployer
        return VolcanoDeployer(self.verbose)
    elif deployer == "seldon":
        from scanflow.deployer.seldonDeployer import SeldonDeployer
        return SeldonDeployer(self.verbose)
    else:
        raise ValueError("unknown deployer: " + deployer)