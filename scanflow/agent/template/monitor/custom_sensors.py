from fastapi import FastAPI, APIRouter

custom_sensor_router = APIRouter()

@custom_sensor_router.get("/test")
def custom_sensors_root():
    return {"Hello": "custom monitor sensors online"}

def sensor_root():
    return {"Hello": "custom monitor sensors"}