# Scanflow-Kubernetes: An MLOps Platform

Scanflow-Kubernetes is a platform to simplify MLOps. It originally supports deploying and operating on Kubernetes, but users can also extend it into other platforms. 

Scanflow is a high-level library that is built on top of Mlflow. It provides the ability to define workflows, build each node of workflows and agents, and deploy/run the agents/workflows. In addition, it announces a framework for developing agents in order to manage and supervise workflows in both the ML training stage and the inference stage. 

Current components of Scanflow includes:

- **Scanflow Developing**(Scanflow Application): A format for teams defining workflows, agents and basic environment.


- **Scanflow Building**: An API to build Scanflow Application(each node of workflows and agents as containers)


- **Scanflow Deploying**: An API to create a working environment for each team and deploy agents, also provides workflows running as batch workflows or deploying as online services


- **Scanflow Operating**(Scanflow Agent): A framework to develop agents. Provide an online multi-agent system to manage and supervise the workflows.


- **Scanflow Tracking**(Supported by MLflow): Mlflow provides an API to log parameters, artifacts, and models in machine learning experiments. We use mlflow as a database to track these information and transmit the information between teams.


## Scanflow Architecture

![architecture](images/scanflow-architecture.png)

Scanflow Tracker is based on MLflow, MLflow logs can be recorded to local files as default. 

In our private platform, we config PostgreSQL as backend and Minio as artifact stores. For more information regarding how to config [Mlflow with remote tracking server backend and artifact stores](https://www.mlflow.org/docs/latest/tracking.html#scenario-4-mlflow-with-remote-tracking-server-backend-and-artifact-stores)

![tracking-architecture](https://www.mlflow.org/docs/latest/_images/scenario_4.png)

## Installing

Please check [installing](installer/Readme.md) for more details

## MLOps

![architecture](images/architecture.png)

Figure 1: Architecture of MLOps.

The architecture of MLOps is shown in Figure 1. There are many phases and steps required to make the machine learning model in production to provide values. The top describes the steps for the data team and data science team before a model into production. Normally, the data team is responsible for discovering and collecting the valuable data, and the data science team will then develop a machine learning workflow that contains data preparation, validation, and preprocessing, as well as model training, validation, and testing. Workflow manager (e.g., Scanflow) can track the metadata such as metrics and scores and the artifacts during the training phase, analyze them, and automatically tune the hyper-parameters, early stopping and do neural architecture search for improving the model. 
The bottom describes the model in production, including the model inference workflow deployment and the operation phase that automatically manages the machine learning workflow from both the application layer (e.g., workflow manager Scanflow) and the infrastructure layer (e.g., resource manager Kubernetes). 

For deploying and managing the machine learning workflow at scale, the data engineer team should also build a workflow managed by the workflow manager but wrap and deploy the model as a service. From the application layer controlled view, the workflow manager could log the model metrics (such as scores) and artifacts (such as new data) to detect outliers, adversarial or drift and provide model explanations and finally trigger the machine learning workflow to be retrained or the model to be updated. From the infrastructure layer controlled view, allowing the model as a service helps it to be released, updated and rollouted independently, and can monitor the latency and failure rate of its predicted invocations at inference time. With these observations, the resource manager can automatically scale the service to achieve the reliability and efficiency of the model. Here we start the definition of each step, it consists of setting the images, requirements, python scripts, and parameters. This definition is set just once and the behavior of each step can be changed by its parameters. In a production system, this notebook should be run once in order to start the network, tracker, executors, and agents as containers. Then, these containers can be executed or reached on demand by using Scanflow API (e.g. call the online predictor service or execute the inference batch executor).

Scanflow as a shared tool between teams, can help different teams working under the same concept in order to communicate and share the data, models, and artifacts. Also Scanflow deals with the hard point within all the stages, thus can help teams fast and easily develop, build, deploy, and auto-manage their workflows. MNIST project is organized in this way, in the below tutorials we show how different teams use Scanflow.



## Tutorials

Please check the jupyter notebook for more details.

MNIST Project Tutorial: [mnist](tutorials/mnist/Readme.md)

mlperf Project Tutorial: [mlperf](tutorials/mlperf/Readme.md)