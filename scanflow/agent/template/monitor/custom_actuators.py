from scanflow.agent.actuators.actuator import actuator

from typing import List

import mlflow

@actuator(path="/sensors/analyze_check_predictions", depender="checker")
def call_analyze_check_predictions(args, kwargs):
    return args, kwargs