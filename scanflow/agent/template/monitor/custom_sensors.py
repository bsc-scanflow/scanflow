from .custom_rules import *
from .custom_actuators import *
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

from datetime import datetime
import time
from functools import reduce

from scanflow.agent.sensors.sensor import sensor

def tock():
    print('Tock! The time is: %s' %  time.strftime("'%Y-%m-%d %H:%M:%S'"))

#example 1: count number of predictions in last 5 min
@sensor(executors=["predictor"], filter_string="tags.mlflow.runName='predictor-batch' and metrics.n_predictions > 0")
async def count_number_of_predictions(runs: List[mlflow.entities.Run], *args, **kwargs):
    n_predictions = list(map(lambda run: run.data.metrics['n_predictions'], runs))
    
    number_of_predictions = reduce(lambda x,y : x+y, n_predictions)
    logging.info(f"count_number_of_predictions - {number_of_predictions}")

    if number_of_predictions_threshold(number_of_predictions):
       await analyze_predictions(list(map(lambda run: run.info.run_id, runs)))

    return number_of_predictions

