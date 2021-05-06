from fastapi import FastAPI, APIRouter

actuators_router = APIRouter()

@actuators_router.get("/")
def actuator_root():
    return {"Hello": "actuators"}