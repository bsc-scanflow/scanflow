from scanflow.agent.actuators.actuator import actuator

from typing import List
from scanflow.client import ScanflowDeployerClient
from scanflow.client import ScanflowTrackerClient

import mlflow


async def call_run_retrain_workflow(run_id: str, artifact_path="data"):
    #get workflow meta
    trackerClient = ScanflowTrackerClient(verbose=True)
    workflow = trackerClient.download_workflow("mnist", "datascience", "mnist-wf", local_dir="/tmp")
    workflow.executors[0].parameters.update({"run_id": run_id, "path": artifact_path, "fromlocal": True})
    workflow.executors[1].parameters.update({"x_newdata_path":"/workflow/load-data/data/x_newdata.npy","y_newdata_path":"/workflow/load-data/data/y_newdata.npy"})
    workflow.executors[2].parameters.update({"x_newdata_path":"/workflow/load-data/data/x_newdata.npy","y_newdata_path":"/workflow/load-data/data/y_newdata.npy"})

    #platform executor
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
    workflow.executors[0].parameters.update({"run_id": run_id, "path": artifact_path, "fromlocal": True})

    #platform executor
    deployerClient = ScanflowDeployerClient(user_type="incluster",
                                        deployer="seldon")
    #update workflow
    await deployerClient.update_workflow("mnist", "dataengineer", workflow)