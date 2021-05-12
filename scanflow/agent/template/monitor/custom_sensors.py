from .custom_rules import *
from .custom_actuators import *
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

from datetime import datetime
import time

from scanflow.agent.sensors.sensor import sensor

def tock():
    print('Tock! The time is: %s' %  time.strftime("'%Y-%m-%d %H:%M:%S'"))

#example 1: count number of predictions in last 5 min
@sensor(executors=["predictor"], filter_string="tags.mlflow.runName='predictor-batch' and metrics.n_predictions > 0")
async def count_number_of_predictions(run_ids: List[str]):
    logging.info("tracker sensor - count_number_of_predictions")

    if number_of_predictions_threshold(10000):
        await analyze_predictions(run_ids,"a")

