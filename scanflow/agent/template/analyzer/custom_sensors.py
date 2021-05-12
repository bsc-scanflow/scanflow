from .custom_rules import *
from .custom_actuators import *
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

from datetime import datetime
import time

from scanflow.agent.sensors.sensor import sensor

def tock():
    print('Tock! The time is: %s' %  time.strftime("'%Y-%m-%d %H:%M:%S'"))

#custom_sensor_router = APIRouter()


#@custom_sensor_router.get("/test",
#                            status_code= status.HTTP_200_OK)
#example 1: count number of predictions in last 5 min
@sensor(executors=["predictor"], filter_string="", order_by="")
async def count_number_of_predictions(run_ids: List[str]):
    print("sensor"+run_ids[0])
    if rule_number_of_predictions(10000):
        await analyze_predictions(run_ids,"a")

