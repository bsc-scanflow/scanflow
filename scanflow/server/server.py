import json
import uvicorn
import logging

from fastapi import FastAPI

#scanflow
from scanflow.deployer.deployer import Deployer
from scanflow.deployer.argoDeployer import ArgoDeployer
from scanflow.deployer.volcanoDeployer import VolcanoDeployer
from scanflow.deployer.seldonDeployer import SeldonDeployer

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


app = FastAPI(title='Scanflow API',
              description='Scanflow Server.',
              )


## scanflow app

@app.post("/submit/scanflowApplication",
          tags=['ScanflowApplication'],
          summary="Save scanflow application metadata")
async def save_scanflowApplication(scanflowApp: str):
    """
      scanflowApp: scanflowapplication json file
    """
    response = ""
    return response

@app.post("/list/"

)
async def list_scanflowApplication(app_name, team_name):
    """
    """
    response = ""
    return response


## scanflow app environment
@app.post("/create_environment",
           tag=['Environment'],
           summary="create environment for scanflow app")
async def create_environment(app_name, team_name):
    deployer = Deployer()
    result = deployer.create_environment(app)
    return {"success": result}

@app.post("/clean_environment",
           tag=['Environment'],
           summary="clean environment for scanflow app")
async def clean_environment(app_name, team_name):

    return {}


## scanflow workflow deployer operations
async def build_workflows():
    response = ""
    return response

async def run_workflows():
    response = ""
    return response

async def delete_workflows():
    response = ""
    return response