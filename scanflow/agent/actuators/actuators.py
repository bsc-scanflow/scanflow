from fastapi import FastAPI, APIRouter
from scanflow.agent.config.settings import settings
from scanflow.agent.config.httpClient import http_client

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

actuators_router = APIRouter(prefix="/actuators")

@actuators_router.on_event("startup")
async def actuators_startup():
    logging.info(f"{settings.AGENT_NAME} actuators startup")
    http_client.start()
    
@actuators_router.on_event("shutdown")
async def actuators_shutdown():
    logging.info(f"{settings.AGENT_NAME} actuators shutdown")
    http_client.stop()

if settings.AGENT_TYPE == "monitor":
    from scanflow.agent.template.monitor import actuators
    actuators_router.include_router(actuators.monitor_actuators_router)
elif settings.AGENT_TYPE == "analyzer":
    from scanflow.agent.template.analyzer import actuators
    actuators_router.include_router(actuators.analyzer_actuators_router)
elif settings.AGENT_TYPE == "planner":
    from scanflow.agent.template.planner import actuators
    actuators_router.include_router(actuators.planner_actuators_router)
elif settings.AGENT_TYPE == "executor":
    from scanflow.agent.template.executor import actuators
    actuators_router.include_router(actuators.executor_actuators_router)
else:
    #custom agent actuators
    from scanflow.agent.actuators import custom_actuators
    actuators_router.include_router(actuators.custom_actuators_router)