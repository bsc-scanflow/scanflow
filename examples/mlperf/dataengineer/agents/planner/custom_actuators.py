from typing import Any
from scanflow.agent.actuators.actuator import actuator

import logging
from scanflow.agent.config.httpClient import http_client
from scanflow.server.schemas.app import Workflow
import json

from scanflow.client.scanflowDeployerClient import ScanflowDeployerClient

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#ok!
async def call_run_workflow_affinity(app_name : str,
                                     team_name : str,
                                     workflow : Workflow,
                                     antipodaffinity: dict,
                                     deployer : str):
    #get workflow meta
    workflow.affinity = antipodaffinity
    logging.info(f"workflownew: {workflow.dict()}")

    #deploy workflow
    url = f"http://scanflow-server-service.scanflow-system.svc.cluster.local/deployer/run_workflow/{app_name}/{team_name}?deployer={deployer}"
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
    
#ok!
async def call_deploy_workflow_replicas(app_name : str,
                                        team_name : str,
                                        workflow : Workflow,
                                        kedaconfig : dict,
                                        replicas : int,
                                        deployer :str):
    
    #get workflow meta
    workflow.kedaSpec = kedaconfig
    logging.info(f"workflownew: {workflow.dict()}")
    
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
    
async def call_deploy_workflow_backupservice(app_name : str,
                                        team_name : str,
                                        workflow : Workflow,
                                        backupservice : dict,
                                        replicas : int,
                                        deployer :str):

    logging.info(f"workflownew: {workflow.dict()}")

    #deploy workflow
    url = f"http://scanflow-server-service.scanflow-system.svc.cluster.local/deployer/deploy_workflow/{app_name}/{team_name}?replicas={replicas}&deployer={deployer}&backupservice={backupservice}"
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
    
    
#ok!
async def call_update_traffic(app_name : str,
                              team_name : str,
                              name: str,
                              patch: dict,
                              deployer :str):

    logging.info(f"patch: {patch}")

    #deploy workflow
    url = f"http://scanflow-server-service.scanflow-system.svc.cluster.local/deployer/update_traffic/{app_name}/{team_name}/{name}?deployer={deployer}"
    async with http_client.session.post(url, 
                                        data = json.dumps(patch),
                                        headers={'Content-Type':'application/json'}) as response:
                status = response.status
                text = await response.json()
    logging.info(f"{text['detail']}")
    if status == 200:
        return True
    else:
        return False
    
    
async def find_available_replicas(url):
    #deploy workflow
    url = url
    async with http_client.session.get(url, 
                                        headers={'Content-Type':'application/json'}) as response:
                status = response.status
                text = await response.json()
    logging.info(f"response: {text['data']}")
    if status == 200:
        return text["data"]["result"][0]["value"][1]
    else:
        return -1