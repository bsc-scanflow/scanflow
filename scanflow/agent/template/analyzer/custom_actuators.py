from scanflow.agent.actuators.actuator import actuator

from typing import List
from scanflow.client import ScanflowDeployerClient
from scanflow.client import ScanflowTrackerClient

import mlflow


async def call_run_analyze_workflow(run_id: str, artifact_path:str):
    #get workflow
    trackerClient = ScanflowTrackerClient(verbose=True)
    workflow = trackerClient.download_workflow("mnist", "dataengineer", "detector-inference", local_dir="/tmp")
    workflow.executors[0].parameters = {'run_id': run_id, 'path': artifact_path, 'fromlocal': True}
    
    #platform executor
    deployerClient = ScanflowDeployerClient(user_type="incluster",
                                        deployer="argo")
    #run workflow
    await deployerClient.run_workflow("mnist", "dataengineer", workflow)

@actuator(path="/sensors/plan_retain_model", depender="planner")
def call_plan_retrain_model(args, kwargs):
    return args, kwargs