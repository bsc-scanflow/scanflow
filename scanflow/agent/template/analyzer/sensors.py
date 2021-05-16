#general
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


#fastapi
from fastapi import FastAPI, APIRouter, Depends
from fastapi import Response, status, HTTPException


#scanflow
from scanflow.agent.config.settings import settings
from scanflow.agent.template.monitor import custom_sensors
from scanflow.agent.schemas.sensor import Sensor, SensorOutput, Trigger
from scanflow.agent.sensors.sensor_dependency import sensor

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))


analyzer_sensors_router = APIRouter(tags=['analyzer sensors'])

try:
    analyzer_sensors_router.include_router(custom_sensors.custom_sensor_router, tags=["custom sensors"])
except:
    logging.info("custom_sensors function does not provide a router.")


@analyzer_sensors_router.get("/",
                            status_code= status.HTTP_200_OK)
async def sensors_root():
    print(f"Hello! analyzer sensors")
    return {"Hello": "analyzer sensors"}

@analyzer_sensors_router.get("/detail",
                            status_code= status.HTTP_200_OK)
async def sensors_detail():
    return {"detail": "analyzer sensors"}



@analyzer_sensors_router.post("/analyze_predictions",
                            status_code= status.HTTP_200_OK)
async def sensors_analyze_predictions(runs: str = Depends(sensor)):
    #print(request.run_ids)
    #print(request.args)
    #print(request.kwargs)
    print(runs[0])


    return {"detail": "analyzed predictions"}