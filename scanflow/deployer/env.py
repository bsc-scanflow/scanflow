from typing import Optional, List, Dict

class ScanflowSecret():
    AWS_ACCESS_KEY_ID : Optional[str] = "scanflow"
    AWS_SECRET_ACCESS_KEY : Optional[str] = "scanflow123"
    MLFLOW_S3_ENDPOINT_URL : Optional[str] = "http://minio.scanflow-server.svc.cluster.local"
    AWS_ENDPOINT_URL: Optional[str] = "http://minio.scanflow-server.svc.cluster.local"

class ScanflowTrackerConfig():
    TRACKER_STORAGE: Optional[str] = "postgresql://postgres:scanflow123@scanflow-postgres.scanflow-server.svc.cluster.local/scanflow-default"
    TRACKER_ARTIFACT: Optional[str] = "s3://scanflow-default"

class ScanflowClientConfig():
    SCANFLOW_TRACKER_URI : Optional[str] = "http://scanflow-tracker-service.scanflow-server.svc.cluster.local"
    SCANFLOW_SERVER_URI : Optional[str] = "http://scanflow-server-service.scanflow-server.svc.cluster.local"
    SCANFLOW_TRACKER_LOCAL_URI : Optional[str] = "http://scanflow-tracker.scanflow-default.svc.cluster.local"

class ScanflowEnvironment():
    namespace: Optional[str] = "scanflow-default" 
    #role: now we start with default
    #secret
    secret : Optional[ScanflowSecret] = ScanflowSecret()
    #secret_stringData : Optional[dict] = {
    #    "AWS_ACCESS_KEY_ID": "admin", 
    #    "AWS_SECRET_ACCESS_KEY": "admin123", 
    #    "MLFLOW_S3_ENDPOINT_URL": "http://minio.minio-system.svc.cluster.local:9000" 
    #}
    #configmap tracker
    tracker_config : Optional[ScanflowTrackerConfig] = ScanflowTrackerConfig()
    #configmap_tracker_data : Optional[dict] = {
    #    "TRACKER_STORAGE": "postgresql://scanflow:scanflow123@postgresql-service.postgresql.svc.cluster.local/scanflow-default",
    #    "TRACKER_ARTIFACT": "s3://scanflow-default"
    #}
    #configmap client
    client_config : Optional[ScanflowClientConfig] = ScanflowClientConfig()
    #configmap_remotescanflow_data : Optional[dict] = {
    #    "SCANFLOW_TRACKER_URI" : "http://scanflow-tracker-service.scanflow-system.svc.cluster.local",
    #    "SCANFLOW_SERVER_URI" : "http://scanflow-server-service.scanflow-system.svc.cluster.local"
    #}
    #configmap_localscanflow_data : Optional[dict] = {
    #    "SCANFLOW_TRACKER_LOCAL_URI" : "http://scanflow-tracker.scanflow-default.svc.cluster.local"
    #}




