from fastapi import APIRouter

from scanflow.agent.sensors import sensors
from scanflow.agent.rules import rules
from scanflow.agent.actuators import actuators

agent_router = APIRouter()
agent_router.include_router(sensors.sensors_router)
agent_router.include_router(rules.rules_router)
agent_router.include_router(actuators.actuators_router)

