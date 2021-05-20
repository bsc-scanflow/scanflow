import json
import logging
from typing import Optional

import sys
import os
sys.path.insert(0,'../..')

#fastapi
from fastapi import FastAPI

# routers
from scanflow.server.routers import scanflowApplication
from scanflow.server.routers import scanflowModel
from scanflow.server.routers import scanflowDeployer

#dependencies
from scanflow.server.dependencies import get_tracker

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


app = FastAPI(title='Scanflow API',
              description='Scanflow Server.')


app.include_router(
    scanflowApplication.router,
    tags=['scanflowApplication'],
    prefix="/app"
)

app.include_router(
    scanflowModel.router,
    tags=['scanflowModel'],
    prefix="/model"
)

app.include_router(
    scanflowDeployer.router,
    tags=['scanflowDeployer'],
    prefix="/deployer"
)


@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass




