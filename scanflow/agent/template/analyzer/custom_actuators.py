from scanflow.agent.actuators.actuator import actuator

from typing import List

import mlflow

@actuator(path="/deployer/run_workflow", depender="scanflow")
def call_run_analyze_workflow(args, kwargs):
    return args, kwargs

@actuator(path="/sensors/plan_retain_model", depender="retainer")
def call_plan_retrain_model(args, kwargs):
    return args, kwargs