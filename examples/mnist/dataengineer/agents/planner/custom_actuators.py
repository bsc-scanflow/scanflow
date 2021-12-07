from scanflow.agent.actuators.actuator import actuator

from typing import List
from scanflow.client import ScanflowDeployerClient
from scanflow.client import ScanflowTrackerClient

import logging
from scanflow.agent.config.httpClient import http_client
from scanflow.server.schemas.app import Workflow
import json


import mlflow


async def call_run_retrain_workflow(run_id: str, artifact_path="data"):
    #get workflow meta
    trackerClient = ScanflowTrackerClient(verbose=True)
    workflow = trackerClient.download_workflow("mnist", "datascience", "mnist-wf", local_dir="/tmp")
    workflow.nodes[0].parameters.update({"run_id": run_id, "path": artifact_path, "fromlocal": True})
    workflow.nodes[1].parameters.update({"x_newdata_path":"/workflow/load-data/data/x_newdata.npy","y_newdata_path":"/workflow/load-data/data/y_newdata.npy"})
    workflow.nodes[2].parameters.update({"x_newdata_path":"/workflow/load-data/data/x_newdata.npy","y_newdata_path":"/workflow/load-data/data/y_newdata.npy"})

    #platform nodes
    deployerClient = ScanflowDeployerClient(user_type="incluster",
                                        deployer="argo")
    #run workflow
    await deployerClient.run_workflow("mnist", "dataengineer", workflow)

@actuator(path="/sensors/executor_transit_model", depender="executor")
def call_executor_transit_model(args, kwargs):
    return args, kwargs

async def call_update_workflow(run_id: str, artifact_path="data"):
    #get workflow meta
    trackerClient = ScanflowTrackerClient(verbose=True)
    workflow = trackerClient.download_workflow("mnist", "dataengineer", "online-inference", local_dir="/tmp")
    workflow.nodes[0].parameters.update({"run_id": run_id, "path": artifact_path, "fromlocal": True})

    #platform nodes
    deployerClient = ScanflowDeployerClient(user_type="incluster",
                                        deployer="seldon")
    #update workflow
    await deployerClient.update_workflow("mnist", "dataengineer", workflow)
    
    
#ok!
async def call_deploy_workflow_replicas(app_name : str,
                                        team_name : str,
                                        workflow : Workflow,
                                        kedaconfig : dict,
                                        replicas : int,
                                        deployer :str):
    
    #get workflow meta
    workflow.kedaSpec = kedaconfig
    
    #deploy workflow
    url = f"http://scanflow-server-service.scanflow-system.svc.cluster.local/deployer/deploy_workflow/{app_name}/{team_name}?replicas={replicas}&deployer={deployer}"
    async with http_client.session.post(url, 
                                        data=json.dumps(workflow.dict()),
                                        headers={'Content-Type':'application/json'}) as response:
                status = response.status
                text = await response.json()
    logging.info(f"{text['detail']}")
    if status == 200:
        return True
    else:
        return False