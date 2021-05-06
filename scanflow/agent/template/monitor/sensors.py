from fastapi import FastAPI, APIRouter
from scanflow.agent.config.settings import settings

from scanflow.agent.template.monitor import custom_sensors

monitor_sensors_router = APIRouter()
try:
    monitor_sensors_router.include_router(custom_sensors.custom_sensor_router)
except:
    print("custom function does not provide a router")

@monitor_sensors_router.get("/")
def sensors_root():
    return settings.special_function[0]()

