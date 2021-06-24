from fastapi import FastAPI, APIRouter
from scanflow.agent.config.settings import settings

sensors_router = APIRouter(prefix="/sensors")

from scanflow.agent.sensors import sensors_trigger
sensors_router.include_router(sensors_trigger.sensors_trigger_router, prefix="/event", tags=["auto-triggered sensors"])


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
    #custom agent sensor
    from scanflow.agent.sensors import custom_sensors
    sensors_router.include_router(sensors.custom_sensors_router, tags=["custom sensors"])