from fastapi import APIRouter
from fastapi import FastAPI, Response, status, HTTPException

from ..schemas.app import Application

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

router = APIRouter()

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

## scanflow app meta
## save/load/update scanflow application
@router.post("/submit",
          summary = "Save scanflow application metadata",
          status_code = status.HTTP_201_CREATED)
async def save_scanflowApplication(app: Application, response: Response):
    """
      app: scanflowapplication json 
    """
    logging.info(f"call save_scanflowApplication {app.dict()} ")
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
    
    try:
        mlflow.set_experiment(app.app_name)
        with mlflow.start_run(run_name=f"scanflow-app-{app.team_name}"):
            artifact_uri = mlflow.get_artifact_uri()
            logging.info("save app to artifact uri: {}".format(artifact_uri))
            mlflow.log_dict(app.dict(), "{}/{}.json".format(app.team_name, app.app_name))
            if app.workflows is not None:
                for workflow in app.workflows:
                    mlflow.log_dict(workflow.dict(), "{}/workflows/{}.json".format(app.team_name, workflow.name))
            if app.agents is not None:
                for agent in app.agents:
                    mlflow.log_dict(agent.dict(), "{}/agents/{}.json".format(app.team_name, agent.name))
        return {'detail': f"app is saved into {artifact_uri}"}
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="mlflow exception")

#@app.post("/list/scanflowApplications",
#          tags=['ScanflowApplication'],
#          summary="List all scanflow application")
#async def list_scanflowApplication(app_name, team_name):
#    """
#    """
#    response = ""
#    return response
#