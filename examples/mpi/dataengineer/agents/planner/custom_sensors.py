from select import select
from scanflow.server.schemas.app import Workflow
from .custom_rules import *
from .custom_actuators import *
import numpy as np
from typing import List, Optional
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#fastapi
from fastapi import FastAPI, APIRouter, Depends
from fastapi import Response, status, HTTPException

from datetime import datetime
import time

from scanflow.agent.sensors.sensor import sensor
from scanflow.agent.sensors.sensor_dependency import sensor_dependency


custom_sensor_router = APIRouter()


@custom_sensor_router.post("/run_autoconfig_workflow/{app_name}/{team_name}",
                           status_code= status.HTTP_200_OK)
async def sensors_run_autoconfig_workflow(app_name: str,
                                          team_name: str,
                                          workflow: Workflow,
                                          deployer: Optional[str]="volcano"):
    if workflow.type == "mpi":
        for node in workflow.nodes:
            
            strategy = select_strategy(node.plugins)
            if strategy=="granularity":
                node = enable_granularity_strategy(node)
            else:
                logging.info(f"cannot find suitable strategy")
           
            await call_run_workflow(app_name=app_name,
                                    team_name=team_name,
                                    workflow=workflow,
                                    deployer=deployer)
                
    
    return {"detail": "sensors_run_autoconfig_workflow received"}


    


