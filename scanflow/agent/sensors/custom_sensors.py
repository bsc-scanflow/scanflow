from fastapi import FastAPI, APIRouter

custom_sensor_router = APIRouter()

@custom_sensor_router.get("/online")
async def track_new_data_sensor():
    return {"Hello": "custom sensors online(without using template)"}