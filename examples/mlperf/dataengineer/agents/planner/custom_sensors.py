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

@custom_sensor_router.post("/deploy_autoconfig_workflow/{app_name}/{team_name}",
                           status_code= status.HTTP_200_OK)
async def sensors_deploy_autoconfig_workflow(app_name: str,
                                             team_name: str,
                                             workflow: Workflow,
                                             replicas: Optional[int] = 1,
                                             deployer: Optional[str]="seldon"):
    kedaconfig = find_scaling_config()
    if kedaconfig is not None:
        await call_deploy_workflow_replicas(app_name=app_name,
                                            team_name=team_name,
                                            workflow=workflow, 
                                            kedaconfig=kedaconfig,
                                            replicas=replicas,
                                            deployer=deployer)
    else:
        logging.info(f"cannot find scaling config")
    
    return {"detail": "sensors_deploy_autoconfig_workflow received"}


@custom_sensor_router.post("/run_autoconfig_workflow/{app_name}/{team_name}",
                           status_code= status.HTTP_200_OK)
async def sensors_run_autoconfig_workflow(app_name: str,
                                          team_name: str,
                                          workflow: Workflow,
                                          deployer: Optional[str]="argo"):
    antipodaffinity = find_antiaffinity_config()
    if antipodaffinity is not None:
        await call_run_workflow_affinity(app_name=app_name,
                                            team_name=team_name,
                                            workflow=workflow, 
                                            antipodaffinity=antipodaffinity,
                                            deployer=deployer)
    else:
        logging.info(f"cannot find affinity config")
    
    return {"detail": "sensors_run_autoconfig_workflow received"}



@custom_sensor_router.post("/deploy_backuped_workflow/{app_name}/{team_name}",
                           status_code= status.HTTP_200_OK)
async def sensors_deploy_autoconfig_workflow(app_name: str,
                                             team_name: str,
                                             workflow: Workflow,
                                             replicas: Optional[int] = 1,
                                             deployer: Optional[str]="seldon"):
    backupservice = find_backup_service()
    if backupservice is not None:
        await call_deploy_workflow_backupservice(app_name=app_name,
                                                 team_name=team_name,
                                                 workflow=workflow, 
                                                 backupservice=backupservice,
                                                 replicas=replicas,
                                                 deployer=deployer)
    else:
        logging.info(f"cannot find backupservice config")
    
    return {"detail": "sensors_deploy_backuped_workflow received"}
    

@custom_sensor_router.post("/testtraffic",
                           status_code= status.HTTP_200_OK)
async def sensors_get_availability(app_name: str,
                                     team_name: str,
                                     name: str,
                                     deployer: Optional[str]="seldon"):
    #need to use scanflow trigger to check the number of available replicas.
    # curl -g 'http://172.30.0.50:30002/api/v1/query?query=sum(kube_deployment_status_replicas{namespace=~"scanflow-mlperf-dataengineer",deployment=~"seldon.*"})i'
    while True:
        availreplicas = await find_available_replicas("http://prometheus.istio-system.svc.cluster.local:9090/api/v1/query?query=sum(kube_deployment_status_replicas{namespace=~\"scanflow-mlperf-dataengineer\",deployment=~\"seldon.*\"})")
        
        patch = check_availability(availreplicas, name)
        if patch:
            await call_update_traffic(app_name=app_name,
                                      team_name=team_name,
                                      name=f"{name}-grpc", 
                                      patch=patch,
                                      deployer=deployer)
            break
        else:
            logging.info(f"service is available")
        time.sleep(30)
    
    return {"detail": "sensors_deploy_backuped_workflow received"}
