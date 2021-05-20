from scanflow.agent.actuators.actuator import actuator

from typing import List
from scanflow.client import ScanflowDeployerClient

import mlflow


def call_run_analyze_workflow(run_id: str):
    #platform executor
    deployerClient = ScanflowDeployerClient(user_type="incluster",
                                        deployer="argo")
    #get workflow meta
    deployerClient.download
    #run workflow
    deployerClient.run_workflow("mnist", "dataengineer", workflow)


@actuator(path="/sensors/plan_retain_model", depender="retainer")
def call_plan_retrain_model(args, kwargs):
    return args, kwargs