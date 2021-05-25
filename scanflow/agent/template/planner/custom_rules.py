from scanflow.client import ScanflowTrackerClient
import mlflow
from mlflow.tracking import MlflowClient
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(True))

def better_model(run: mlflow.entities.Run):
    mlflowClient = MlflowClient(client.get_tracker_uri(True))
    mv = mlflowClient.get_latest_versions("mnist_cnn", stages=["Production"])
    run_current = mlflow.get_run(mv[0].run_id)
    return run.data.metrics['accuracy'] > run_current.data.metrics['accuracy']