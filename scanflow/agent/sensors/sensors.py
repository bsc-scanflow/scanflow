from fastapi import FastAPI, APIRouter
from scanflow.agent.config.settings import settings

sensors_router = APIRouter()

if settings.AGENT_TYPE == "monitor":
    from scanflow.agent.template.monitor import sensors
    sensors_router.include_router(sensors.monitor_sensors_router)
elif settings.AGENT_TYPE == "analyzer":
    from scanflow.agent.template.analyzer import sensors
    sensors_router.include_router(sensors.analyzer_sensors_router)
elif settings.AGENT_TYPE == "planner":
    from scanflow.agent.template.planner import sensors
    sensors_router.include_router(sensors.planner_sensors_router)
elif settings.AGENT_TYPE == "executor":
    from scanflow.agent.template.executor import sensors
    sensors_router.include_router(sensors.executor_sensors_router)
else:
    @router.get("/")
    def sensors_root():
       return {"Hello sensors": "unknown agent type"}