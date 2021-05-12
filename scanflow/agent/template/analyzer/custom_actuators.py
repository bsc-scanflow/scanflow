from scanflow.agent.actuators.actuator import actuator

from typing import List

import mlflow

#@actuator(path="/sensors/analyze_number_of_pictures", depender="checker")
#def analyze_number_of_pictures(runs: List(mlflow.entities.Run)):
#    pass

@actuator(path="sensors", depender="checker")
def analyze_predictions(response):
    print("analyze_predictions")
    pass