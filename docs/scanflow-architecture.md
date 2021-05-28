
## Scanflow Architecture

![architecture](../images/scanflow-architecture.png)

Scanflow Tracker is based on MLflow, MLflow logs can be recorded to local files as default. 

In our private platform, we config PostgreSQL as backend and Minio as artifact stores. For more information regarding how to config [Mlflow with remote tracking server backend and artifact stores](https://www.mlflow.org/docs/latest/tracking.html#scenario-4-mlflow-with-remote-tracking-server-backend-and-artifact-stores)

![tracking-architecture](https://www.mlflow.org/docs/latest/_images/scenario_4.png)
