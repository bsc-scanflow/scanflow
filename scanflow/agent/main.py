from fastapi import FastAPI

import sys
import os
sys.path.insert(0,'../..')

from scanflow.agent.config.settings import settings
from scanflow.agent import agent_router


agent = FastAPI(
    title=f"{settings.AGENT_NAME} Agent API", 
    description=f"{settings.AGENT_NAME} Agent API")

agent.include_router(agent_router.agent_router)

