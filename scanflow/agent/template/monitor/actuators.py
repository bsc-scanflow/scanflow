import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

monitor_actuators_router = APIRouter(tags=['monitor actuators'])

@monitor_actuators_router.get("/",
                            status_code= status.HTTP_200_OK)
async def actuators_root():
    print(f"Hello! monitor actuators")
    return {"Hello": "monitor actuators"}

#custom
from scanflow.agent.template.monitor import custom_actuators
try:
    monitor_actuators_router.include_router(custom_actuators.custom_actuators_router, tags=["custom actuators"])
except:
    logging.info("custom_actuators function does not provide a router.")

#scanflow monitor actuator
def analyze_number_of_pictures(number_of_pictures: int):
    if number_of_pictures > 20:
        print("yes")