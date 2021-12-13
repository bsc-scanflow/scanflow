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


def find_scaling_config(requirement):#requirement=2
    
    #keda scaler
    trigger_request_rate = client.ScalerTriggerPrometheus(
        serverAddress = 'http://prometheus.istio-system:9090',
        metricName = 'istio_requests_total',
        query = 'sum(rate(istio_requests_total{connection_security_policy="mutual_tls",destination_service=~"online-inference-online-inference.scanflow-mnist-dataengineer.svc.cluster.local",reporter=~"destination",source_workload=~"istio-ingressgateway",source_workload_namespace=~"istio-system"}[5m]))',
        threshold = f'\'{requirement}\'',
    )

    kedaSpec = client.KedaSpec(maxReplicaCount=10,
                           minReplicaCount=3,
                           pollingInterval=10,
                           cooldownPeriod=10,
                           triggers=[trigger_request_rate])

    return kedaSpec.to_dict()
