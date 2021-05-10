#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

analyzer_actuators_router = APIRouter(tags=['analyzer actuators'])

@analyzer_actuators_router.get("/",
                            status_code= status.HTTP_200_OK)
async def actuators_root():
    print(f"Hello! analyzer actuators")
    return {"Hello": "analyzer actuators"}