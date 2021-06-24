#general
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


#fastapi
from fastapi import FastAPI, APIRouter, Depends
from fastapi import Response, status, HTTPException

analyzer_sensors_router = APIRouter(tags=['analyzer sensors'])

#custom
try:
    from scanflow.agent.template.analyzer import custom_sensors
    analyzer_sensors_router.include_router(custom_sensors.custom_sensor_router, tags=["custom sensors"])
except:
    logging.info("custom_sensors function does not provide a router.")


@analyzer_sensors_router.get("/",
                            status_code= status.HTTP_200_OK)
async def sensors_root():
    print(f"Hello! analyzer sensors")
    return {"Hello": "analyzer sensors"}



