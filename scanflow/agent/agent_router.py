from fastapi import APIRouter

from scanflow.agent.sensors import sensors
from scanflow.agent.rules import rules
from scanflow.agent.actuators import actuators

agent_router = APIRouter()
agent_router.include_router(sensors.sensors_router, prefix="/sensors", tags=["sensors"])
agent_router.include_router(rules.rules_router, prefix="/rules", tags=["rules"])
agent_router.include_router(actuators.actuators_router, prefix="/actuators", tags=["actuators"])

