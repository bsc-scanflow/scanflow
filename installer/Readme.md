## Scanflow-Kubernetes 

Scanflow-Kubernetes is a web service deployed on Kubernetes. It provides a framework for managing and supervising a machine learning workflow in both the training stage and the inference stage. currently feature of scanflow includes:

1. workflow definition,
2. multi-agent system for supervising workflows,
3. different deploying backend - k8s, argo, seldon

## Prerequisites

deploy-backend
- Kubernetes 1.12+ 
- Argo 3.0+
- Seldon-core 0.5+

tracker(mlflow)
- artifact store - Minio
- backend store - PostgreSQL

# Building scanflow controller by dockerfile

You can use the provided [Dockerfile](dockerfile/Dockerfile)

```bash
$ docker build -f dockerfile/controller/Dockerfile -t 172.30.0.49:5000/scanflow-controller .
$ docker push 172.30.0.49:5000/scanflow-controller

$ docker build -f dockerfile/tracker/Dockerfile -t 172.30.0.49:5000/scanflow-tracker .
$ docker push 172.30.0.49:5000/scanflow-tracker
```

| Service|cluster host ip|Port|NodePort|
|----------------|-----------------|----------------|-------------|
|`Scanflow server`| 172.30.0.50 | 8080 | 46666 |
|`Scanflow tracker(mlflow)`|  172.30.0.50 | 8080 | 46667 |

## Installing kubernetes via helm charts

To install the scanflow with chart:

create scanflow-kubernetes namespace

```bash
kubectl create namespace scanflow-system
```

```bash
helm install helm/chart --namespace <namespace> --name <specified-name>

e.g :
helm install helm/chart --namespace scanflow-system --name scanflow-release
```

This command deploys scanflow in kubernetes cluster with default configuration.  The [configuration](#configuration) section lists the parameters that can be configured during installation.


## Uninstalling the Chart

```bash
$ helm delete --namespace scanflow-system scanflow-release --purge
```

## Configuration

The following are the list configurable parameters of Volcano Chart and their default values.

| Parameter|Description|Default Value|
|----------------|-----------------|----------------------|
|`basic.image_tag_version`| Docker image version Tag | `latest`|
|`basic.scanflow_controller_image_name`|Controller Docker Image Name|`172.30.0.49/scanflow-controller`|
|`basic.scanflow_tracker_image_name`|Controller Docker Image Name|`172.30.0.49/scanflow-tracker`|
|`basic.image_pull_policy`|Image Pull Policy|`IfNotPresent`|
|`trakcer.scanflow_trakcer_storage_backend`|||
|`trakcer.scanflow_trakcer_storage_url`|||
|`trakcer.scanflow_trakcer_storage_username`|||
|`trakcer.scanflow_trakcer_storage_password`|||
|`trakcer.scanflow_trakcer_artifact_backend`|||
|`trakcer.scanflow_trakcer_artifact_url`|||
|`trakcer.scanflow_trakcer_artifact_username`|||
|`trakcer.scanflow_trakcer_artifact_password`|||
to change each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example,

```bash
$ helm install --name scanflow-release --set basic.image_pull_policy=Always scanflow-system/scanflow
```

The above command set image pull policy to `Always`, so docker image will be pulled each time.


Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example,

```bash
$ helm install --name scanflow-release -f values.yaml scanflow-system/scanflow
```

> **Tip**: You can use the default [values.yaml](helm/chart/values.yaml)
