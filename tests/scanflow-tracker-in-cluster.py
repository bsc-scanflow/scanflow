import sys
import os
sys.path.insert(0,'..')

import scanflow
from scanflow.client import ScanflowTrackerClient

def set_env_vars():
    #os.environ["MLFLOW_URL"] = "http://172.30.0.50:46667"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://10.104.29.93:9000"
    os.environ["AWS_ACCESS_KEY_ID"] = "admin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "admin123"

if __name__ == "__main__":
    print("Running the test script ...")
    set_env_vars()
    client = ScanflowTrackerClient()
    #client.download_app(app_name="mnist", 
    #                team_name="data",
    #                local_dir="/")
    client.metric()