from . import custom_rules

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

from datetime import datetime
import time

def tock():
    print('Tock! The time is: %s' %  time.strftime("'%Y-%m-%d %H:%M:%S'"))

