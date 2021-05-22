from fastapi import APIRouter
from fastapi import FastAPI, Response, status, HTTPException

from ..schemas.app import Application, Workflow, Executor
from ..schemas.deploy_env import ScanflowEnvironment

from typing import Optional, List

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
async def run_app(app: Application, deployer: Optional[str]="argo"):
    logging.info(f"app {app.dict()}")

    namespace = f"scanflow-{app.app_name}-{app.team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.run_workflows(namespace, app.workflows)

    if result:
        return {'detail': "all workflows within the application have been submitted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="run app error")

@router.post("/delete_app",
           summary="delete all workflows within the application",
           status_code = status.HTTP_200_OK)
async def delete_app(app: Application, deployer: Optional[str]="argo"):
    namespace = f"scanflow-{app.app_name}-{app.team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.delete_workflows(namespace, app.workflows)
    
    if result:
        return {'detail': "all workflows within the application have been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="delete app error")

@router.post("/run_workflows/{app_name}/{team_name}",
           summary="run workflows",
           status_code = status.HTTP_200_OK)
async def run_workflows(app_name: str,
                        team_name: str,
                        workflows: List[Workflow],
                        deployer: Optional[str]="argo"):
    namespace = f"scanflow-{app_name}-{team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.run_workflows(namespace, workflows)

    if result:
        return {'detail': "all workflows have been submitted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="run workflows error")

@router.post("/delete_workflows/{app_name}/{team_name}",
           summary="delete workflows",
           status_code = status.HTTP_200_OK)
async def delete_workflows(app_name: str,
                        team_name: str,
                        workflows: List[Workflow],
                        deployer: Optional[str]="argo"):
    namespace = f"scanflow-{app_name}-{team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.delete_workflows(namespace, workflows)

    if result:
        return {'detail': "all workflows have been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="delete workflows error")

@router.post("/run_workflow/{app_name}/{team_name}",
           summary="run workflow",
           status_code = status.HTTP_200_OK)
async def run_workflow(app_name: str,
                       team_name: str,
                       workflow: Workflow,
                       deployer: Optional[str]="argo"):
    namespace = f"scanflow-{app_name}-{team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.run_workflow(namespace, workflow)

    if result:
        return {'detail': f"workflow {workflow.name} has been submitted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="run workflow error")

@router.post("/delete_workflow/{app_name}/{team_name}",
           summary="delete workflow",
           status_code = status.HTTP_200_OK)
async def delete_workflow(app_name: str,
                          team_name: str,
                          workflow: Workflow,
                          deployer: Optional[str]="argo"):
    namespace = f"scanflow-{app_name}-{team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.delete_workflow(namespace, workflow)

    if result:
        return {'detail': f"workflow {workflow.name} has been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="delete workflow error")

@router.post("/run_executor/{app_name}/{team_name}/{workflow_name}",
           summary="run executor",
           status_code = status.HTTP_200_OK)
async def run_executor(app_name: str,
                     team_name: str,
                     workflow_name: str,
                     executor: Executor,
                     deployer: Optional[str]="argo"):
    namespace = f"scanflow-{app_name}-{team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.run_executor(namespace, executor)

    if result:
        return {'detail': f"executor {workflow_name}-{executor.name} has been submitted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="run executor error")

@router.post("/delete_executor/{app_name}/{team_name}/{workflow_name}",
           summary="delete executor",
           status_code = status.HTTP_200_OK)
async def delete_executor(app_name: str,
                        team_name: str,
                        workflow_name: str,
                        executor: Executor,
                        deployer: Optional[str]="argo"):
    namespace = f"scanflow-{app_name}-{team_name}"
    deployerbackend = get_deployer(deployer)
    result = deployerbackend.delete_executor(namespace, executor)

    if result:
        return {'detail': f"executor {workflow_name}-{executor.name} has been deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="delete executor error")



def get_deployer(deployer):
    if deployer == "argo":
        from scanflow.deployer.argoDeployer import ArgoDeployer
        return ArgoDeployer()
    elif deployer == "volcano":
        from scanflow.deployer.volcanoDeployer import VolcanoDeployer
        return VolcanoDeployer()
    elif deployer == "seldon":
        from scanflow.deployer.seldonDeployer import SeldonDeployer
        return SeldonDeployer()
    else:
        raise ValueError("unknown deployer: " + deployer)