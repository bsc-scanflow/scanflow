import json
import uvicorn
import logging

from fastapi import FastAPI

#scanflow


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


app = FastAPI(title='Scanflow API',
              description='Scanflow Server.',
              )



## workflow

@app.post("/submit/workflow",
          tags=['Workflow'],
          summary="Save workflow and artifacts by name")
async def save_workflow(wf_name: str):
    response = ""
    return response

async def list_workflow():
    response = ""
    return response


## deployer
@app.post("/get/deployer")
async def get_deployer(deployer: str):
    log = ""
    if deployer == "argo":
        log = "argo deployer exsits"
    elif deployer == "volcano":
        log = "volcano deployer exsits"
    elif deployer == "seldon":
        log = "seldon deployer exists"
    else:
        log = "unknown deployer"

    return {"log":log}

async def build_workflows():
    response = ""
    return response

async def run_workflows():
    response = ""
    return response

async def delete_workflows():
    response = ""
    return response