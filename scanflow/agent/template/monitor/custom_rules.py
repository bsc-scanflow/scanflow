from . import custom_actuators

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

def rule_number_of_pictures(number_of_pictures: int):
    if number_of_pictures > 20:
        pass