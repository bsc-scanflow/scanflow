from . import custom_rules

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

from datetime import datetime
import time

def tock():
    print('Tock! The time is: %s' %  time.strftime("'%Y-%m-%d %H:%M:%S'"))

#example 1: count number of pictures in last 1 hour 
def get_number_of_pictures():
    rule_number_of_picture(21)

#example 2: count failure rate in last 5 minutes