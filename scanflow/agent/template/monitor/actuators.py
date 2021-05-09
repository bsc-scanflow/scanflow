#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

monitor_actuators_router = APIRouter()

@monitor_actuators_router.get("/",
                            status_code= status.HTTP_200_OK)
async def actuators_root():
    print(f"Hello! monitor actuators")
    return {"Hello": "monitor actuators"}