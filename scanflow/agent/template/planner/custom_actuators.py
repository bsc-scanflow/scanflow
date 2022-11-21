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
async def call_run_workflow(app_name : str,
                            team_name : str,
                            workflow : Workflow,
                            deployer : str):
    #run workflow
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
    