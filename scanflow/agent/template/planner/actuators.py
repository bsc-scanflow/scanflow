import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

planner_actuators_router = APIRouter(tags=['planner actuators'])

@planner_actuators_router.get("/",
                            status_code= status.HTTP_200_OK)
async def actuators_root():
    print(f"Hello! planner actuators")
    return {"Hello": "planner actuators"}

#custom
try:
    from scanflow.agent.template.planner import custom_actuators
    planner_actuators_router.include_router(custom_actuators.custom_actuators_router, tags=["custom actuators"])
except:
    logging.info("custom_actuators function does not provide a router.")