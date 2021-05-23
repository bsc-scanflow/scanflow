import os
import mlflow
from mlflow.tracking import MlflowClient

features = "rooms, zipcode, median_price, school_rating, transport"
with open("features.txt", 'w') as f:
    f.write(features)

# Log artifacts
with mlflow.start_run() as run:
    mlflow.log_artifact("features.txt", artifact_path="features")

# Download artifacts
client = MlflowClient()
local_dir = "/tmp/artifact_downloads"
if not os.path.exists(local_dir):
    os.mkdir(local_dir)
#local_path = client.download_artifacts(run.info.run_id, "features", local_dir)
#print("Artifacts downloaded in: {}".format(local_path))
#print("Artifacts: {}".format(os.listdir(local_path)))


local_path = client.download_artifacts(run.info.run_id, "features/features.txt", local_dir)
print(local_path)
#print("Artifacts downloaded in: {}".format(local_path))
#print("Artifacts: {}".format(os.listdir(local_path)))