from fastapi import APIRouter
from fastapi import FastAPI, Response, status, HTTPException

from ..schemas.app import Application

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))

router = APIRouter()

## submit/download scanflow model
## now the model can be submitted and downloaded by scanflow tracker client, we could wrap that in the server
@router.post("/save",
          summary = "Save scanflow model",
          status_code = status.HTTP_201_CREATED)
async def save_scanflowModel(app: Application, response: Response):
    """
      save model
    """
    pass

@router.post("/download",
          summary = "Download scanflow model",
          status_code = status.HTTP_200_OK)
async def download_scanflowModel(app: Application, response: Response):
    pass