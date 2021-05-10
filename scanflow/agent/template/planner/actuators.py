#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

planner_actuators_router = APIRouter(tags=['planner actuators'])

@planner_actuators_router.get("/",
                            status_code= status.HTTP_200_OK)
async def actuators_root():
    print(f"Hello! planner actuators")
    return {"Hello": "planner actuators"}