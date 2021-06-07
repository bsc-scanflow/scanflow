import logging
from scanflow.agent.actuators.actuator import actuator

from typing import List
from scanflow.client import ScanflowDeployerClient
from scanflow.client import ScanflowTrackerClient

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

async def call_run_analyze_workflow(run_id: str, artifact_path:str):
    #get workflow
    trackerClient = ScanflowTrackerClient(verbose=True)
    workflow = trackerClient.download_workflow("mnist", "dataengineer", "detector-inference", local_dir="/tmp")
    workflow.nodes[0].parameters = {'run_id': run_id, 'path': artifact_path, 'fromlocal': True}

    logging.info(f"prepared analyze workflow {workflow.to_dict()}")

    #platform nodes
    deployerClient = ScanflowDeployerClient(user_type="incluster",
                                        deployer="argo")
    #run workflow
    await deployerClient.run_workflow("mnist", "dataengineer", workflow)

@actuator(path="/sensors/plan_retain_model", depender="planner")
def call_plan_retrain_model(args, kwargs):
    return args, kwargs