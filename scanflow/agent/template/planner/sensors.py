#general
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

planner_sensors_router = APIRouter(tags=['planner sensors'])

#custom
try:
    from scanflow.agent.template.planner import custom_sensors
    planner_sensors_router.include_router(custom_sensors.custom_sensor_router, tags=["custom sensors"])
except:
    logging.info("custom_sensors function does not provide a router.")


@planner_sensors_router.get("/",
                            status_code= status.HTTP_200_OK)
async def sensors_root():
    print(f"Hello! planner sensors")
    return {"Hello": "planner sensors"}