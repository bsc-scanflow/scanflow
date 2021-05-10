from fastapi import FastAPI, APIRouter
from scanflow.agent.config.settings import settings

actuators_router = APIRouter(prefix="/actuators")

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