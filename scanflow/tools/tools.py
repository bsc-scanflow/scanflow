# -*- coding: utf-8 -*-
# Author: Gusseppe Bravo <gbravor@uni.pe>
# License: BSD 3 clause

import logging
import os
import datetime
import pandas as pd
import docker
import oyaml as yaml
import time
import requests
import json
import matplotlib.pyplot as plt
import networkx as nx

from textwrap import dedent
from sklearn.datasets import make_classification

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

client = docker.from_env()


def generate_compose(paths, workflows, compose_type='repository'):

    compose_dir = None

    if compose_type == 'repository':
        compose_dic, main_file = compose_template_repo(paths, workflows)
        compose_dir = os.path.join(paths['meta_dir'], 'compose-repository')
    elif compose_type == 'verbose':
        compose_dic, main_file = compose_template_verbose(paths, workflows)
        compose_dir = os.path.join(paths['meta_dir'], 'compose-verbose')
    elif compose_type == 'swarm':
        compose_dic, main_file = compose_template_swarm(paths, workflows)
        compose_dir = os.path.join(paths['meta_dir'], 'compose-swarm')
    else:
        compose_dic, main_file = compose_template_swarm(paths, workflows)
        compose_dir = os.path.join(paths['meta_dir'], 'compose-kubernetes')

    os.makedirs(compose_dir, exist_ok=True)
    compose_path = os.path.join(compose_dir, 'docker-compose.yml')
    main_file_path = os.path.join(compose_dir, 'main.py')

    with open(compose_path, 'w') as f:
        yaml.dump(compose_dic, f, default_flow_style=False)

    with open(main_file_path, 'w') as f:
        f.writelines(main_file)

    logging.info(f'[+] Compose file [{compose_path}] was created successfully.')
    logging.info(f'[+] Main file [{main_file_path}] was created successfully.')
    # else:
    #     logging.info(f'[+] MLproject was found.')
    return compose_path


def compose_template_repo(paths, workflows):

    compose_dic = {
        'version': '3',
        'services': {},
        'networks': {}
    }

    id_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    for workflow in workflows:
        # Executors
        for node in workflow['executors']:
            tracker_dir = os.path.join(paths['tracker_dir'], f"tracker-{workflow['name']}")
            compose_dic['services'].update({
                node['name']: {
                    'image': node['name'],
                    'container_name': f"{node['name']}-{id_date}",
                    'networks': [f"network-{workflow['name']}"],
                    'depends_on': [f"tracker-{workflow['name']}"],
                    'environment': {
                        'MLFLOW_TRACKING_URI': f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
                    },
                    'volumes': [f"{paths['app_dir']}:/app",
                                f"{tracker_dir}:/mlflow"],
                    'tty': 'true'

                }
            })

        # Trackers
        if 'tracker' in workflow.keys():
            tracker_dir = os.path.join(paths['tracker_dir'], f"tracker-{workflow['name']}")
            port = workflow['tracker']['port']
            compose_dic['services'].update({
                f"tracker-{workflow['name']}": {
                    'image': f"tracker-{workflow['name']}",
                    'container_name': f"tracker-{workflow['name']}-{id_date}",
                    'networks': [f"network-{workflow['name']}"],
                    'volumes': [f"{tracker_dir}:/mlflow"],
                    'ports': [f"{port+5}:{port}"]

                }
            })

        # networks
        net_name = f"network_{workflow['name']}"
        compose_dic['networks'].update({net_name: None})

    main_file = generate_main_file(paths['app_dir'], id_date)

    return compose_dic, main_file


def compose_template_verbose(paths, workflows):

    compose_dic = {
        'version': '3',
        'services': {},
        'networks': {}
    }

    id_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    for workflow in workflows:
        # Executors
        for node in workflow['executors']:
            tracker_dir = os.path.join(paths['tracker_dir'], f"tracker-{workflow['name']}")
            compose_dic['services'].update({
                node['name']: {
                    'image': node['name'],
                    'container_name': f"{node['name']}-{id_date}",
                    'networks': [f"network-{workflow['name']}"],
                    'depends_on': [f"tracker-{workflow['name']}"],
                    'environment': {
                        'MLFLOW_TRACKING_URI': f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
                    },
                    'volumes': [f"{paths['app_dir']}:/app",
                                f"{tracker_dir}:/mlflow"],
                    # 'tty': 'true'

                }
            })

        # Trackers
        if 'tracker' in workflow.keys():
            tracker_dir = os.path.join(paths['tracker_dir'], f"tracker-{workflow['name']}")
            port = workflow['tracker']['port']
            compose_dic['services'].update({
                f"tracker-{workflow['name']}": {
                    'image': f"tracker-{workflow['name']}",
                    'container_name': f"tracker-{workflow['name']}-{id_date}",
                    'networks': [f"network-{workflow['name']}"],
                    'volumes': [f"{tracker_dir}:/mlflow"],
                    'ports': [f"{port+5}:{port}"]

                }
            })

        # networks
        net_name = f"network_{workflow['name']}"
        compose_dic['networks'].update({net_name: None})

    main_file = generate_main_file(paths['app_dir'], id_date)

    return compose_dic, main_file


def compose_template_swarm(paths, workflows):

    compose_dic = {
        'version': '3',
        'services': {},
        'networks': {}
    }

    id_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    for workflow in workflows:
        # Executors
        for node in workflow['executors']:
            tracker_dir = os.path.join(paths['tracker_dir'], f"tracker-{workflow['name']}")
            compose_dic['services'].update({
                node['name']: {
                    'image': node['name'],
                    'container_name': f"{node['name']}-{id_date}",
                    'networks': [f"network-{workflow['name']}"],
                    'depends_on': [f"tracker-{workflow['name']}"],
                    'environment': {
                        'MLFLOW_TRACKING_URI': f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
                    },
                    'volumes': [f"{paths['app_dir']}:/app",
                                f"{tracker_dir}:/mlflow"],
                    # 'tty': 'true'

                }
            })

        # Trackers
        if 'tracker' in workflow.keys():
            tracker_dir = os.path.join(paths['tracker_dir'], f"tracker-{workflow['name']}")
            port = workflow['tracker']['port']
            compose_dic['services'].update({
                f"tracker-{workflow['name']}": {
                    'image': f"tracker-{workflow['name']}",
                    'container_name': f"tracker-{workflow['name']}-{id_date}",
                    'networks': [f"network-{workflow['name']}"],
                    'volumes': [f"{tracker_dir}:/mlflow"],
                    'ports': [f"{port+5}:{port}"]

                }
            })

        # networks
        net_name = f"network_{workflow['name']}"
        compose_dic['networks'].update({net_name: None})

    main_file = generate_main_file(paths['app_dir'], id_date)

    return compose_dic, main_file


def generate_dockerfile(folder, dock_type='executor', executor=None, port=None):
    # if len(dockerfile) == 0:
    dockerfile = None
    filename = ''
    if dock_type == 'executor':
        dockerfile = dockerfile_template_executor(executor)
        filename = f"Dockerfile_{executor['name']}"
    elif dock_type == 'tracker':
        dockerfile = dockerfile_template_tracker(port)
        filename = f"Dockerfile_tracker_{executor['name']}"
    elif dock_type == 'tracker_agent':
        dockerfile = dockerfile_template_tracker_agent(port)
        filename = f"Dockerfile_tracker_agent_{executor['name']}"
    elif dock_type == 'checker':
        dockerfile = dockerfile_template_checker(port)
        filename = f"Dockerfile_checker_{executor['name']}"
    elif dock_type == 'checker_agent':
        dockerfile = dockerfile_template_checker_agent(port)
        filename = f"Dockerfile_checker_agent_{executor['name']}"
    elif dock_type == 'improver_agent':
        dockerfile = dockerfile_template_improver_agent(port)
        filename = f"Dockerfile_improver_agent_{executor['name']}"
    elif dock_type == 'planner_agent':
        dockerfile = dockerfile_template_planner_agent(port)
        filename = f"Dockerfile_planner_agent_{executor['name']}"

    dockerfile_path = os.path.join(folder, filename)
    with open(dockerfile_path, 'w') as f:
        f.writelines(dockerfile)
    logging.info(f'[+] Dockerfile: [{filename}] was created successfully.')
    # else:
    #     logging.info(f'[+] Dockerfile was found.')

    return dockerfile_path

    # return None


def dockerfile_template_executor(executor):
    # if app_type == 'single':
    template = dedent(f'''
                FROM continuumio/miniconda3

                RUN mkdir /app
                ADD {executor['requirements']} /app
                WORKDIR /app
                RUN pip install -r {executor['requirements']}

                ENTRYPOINT ["python", "/app/{executor['file']}"]
    ''')
    return template


def dockerfile_template_tracker(port=8002):
    # if app_type == 'single':
    template = dedent(f'''
                FROM continuumio/miniconda3
                LABEL maintainer='scanflow'

                ENV MLFLOW_HOME  /mlflow
                ENV MLFLOW_HOST  0.0.0.0
                ENV MLFLOW_PORT  {port}
                ENV MLFLOW_BACKEND  sqlite:////mlflow/backend.sqlite
                ENV MLFLOW_ARTIFACT  /mlflow/mlruns

                RUN pip install mlflow==1.14.1
                RUN mkdir $MLFLOW_HOME
                RUN mkdir -p $MLFLOW_BACKEND
                RUN mkdir -p $MLFLOW_ARTIFACT

                WORKDIR $MLFLOW_HOME

                CMD mlflow server  \
                --backend-store-uri $MLFLOW_BACKEND \
                --default-artifact-root $MLFLOW_ARTIFACT \
                --host $MLFLOW_HOST -p $MLFLOW_PORT

    ''')
    return template

# def dockerfile_template_tracker_agent(port=8003):
#     # if app_type == 'single':
#     template = dedent(f'''
#                 FROM continuumio/miniconda3
#                 LABEL maintainer='scanflow'
#
#                 ENV AGENT_HOME  /mlflow/agent
#                 ENV AGENT_PORT  {port}
#
#                 ENV MLFLOW_HOME  /mlflow
#                 ENV MLFLOW_DIR  /mlflow/mlruns
#
#                 RUN pip install mlflow==1.11.0
#                 RUN pip install fastapi
#                 RUN pip install uvicorn
#                 RUN pip install aiohttp[speedups]
#
#                 RUN mkdir $MLFLOW_HOME
#                 RUN mkdir -p $MLFLOW_DIR
#                 RUN mkdir -p $AGENT_HOME
#
#                 WORKDIR $AGENT_HOME
#
#                 CMD python tracker_agent.py
#
#     ''')
# Eliminate the AGENT_PORT because it is fed in runtime (starting)
def dockerfile_template_tracker_agent(port=8003):
    # if app_type == 'single':
    template = dedent(f'''
                FROM continuumio/miniconda3
                LABEL maintainer='scanflow'

                ENV AGENT_BASE_PATH  /tracker
                ENV AGENT_HOME  /tracker/agent
                ENV AGENT_PORT  {port}

                RUN pip install mlflow==1.14.1
                RUN pip install fastapi
                RUN pip install uvicorn
                RUN pip install aiohttp
                RUN pip install aiodns

                RUN mkdir $AGENT_BASE_PATH
                RUN mkdir -p $AGENT_HOME

                WORKDIR $AGENT_HOME

                CMD uvicorn tracker_agent:app --reload --host 0.0.0.0 --port $AGENT_PORT

    ''')
    return template

def dockerfile_template_checker(port=8004):
    # if app_type == 'single':
    template = dedent(f'''
                FROM continuumio/miniconda3
                LABEL maintainer='scanflow'

                ENV CHECKER_HOME  /checker

                RUN pip install tensorflow==2.4.1
                RUN pip install mlflow==1.14.1
                RUN mkdir $CHECKER_HOME

                WORKDIR $CHECKER_HOME


    ''')
    return template

def dockerfile_template_checker_agent(port=8005):
    # if app_type == 'single':
    template = dedent(f'''
                FROM continuumio/miniconda3
                LABEL maintainer='scanflow'

                ENV AGENT_BASE_PATH  /checker
                ENV AGENT_HOME  /checker/agent
                ENV AGENT_PORT  {port}

                RUN pip install mlflow==1.14.1
                RUN pip install fastapi
                RUN pip install uvicorn
                RUN pip install aiohttp
                RUN pip install aiodns

                RUN mkdir $AGENT_BASE_PATH
                RUN mkdir -p $AGENT_HOME

                WORKDIR $AGENT_HOME

                CMD uvicorn checker_agent:app --reload --host 0.0.0.0 --port $AGENT_PORT

    ''')
    return template

def dockerfile_template_improver_agent(port=8005):
    # if app_type == 'single':
    template = dedent(f'''
                FROM continuumio/miniconda3
                LABEL maintainer='scanflow'

                ENV AGENT_BASE_PATH  /improver
                ENV AGENT_HOME  /improver/agent
                ENV AGENT_PORT  {port}

                RUN pip install mlflow==1.14.1
                RUN pip install fastapi
                RUN pip install uvicorn
                RUN pip install aiohttp
                RUN pip install aiodns

                RUN mkdir $AGENT_BASE_PATH
                RUN mkdir -p $AGENT_HOME

                WORKDIR $AGENT_HOME

                CMD uvicorn improver_agent:app --reload --host 0.0.0.0 --port $AGENT_PORT

    ''')
    return template

def dockerfile_template_planner_agent(port=8005):
    # if app_type == 'single':
    template = dedent(f'''
                FROM continuumio/miniconda3
                LABEL maintainer='scanflow'

                ENV AGENT_BASE_PATH  /planner
                ENV AGENT_HOME  /planner/agent
                ENV AGENT_PORT  {port}

                RUN pip install mlflow==1.14.1
                RUN pip install fastapi
                RUN pip install uvicorn
                RUN pip install aiohttp
                RUN pip install aiodns

                RUN mkdir $AGENT_BASE_PATH
                RUN mkdir -p $AGENT_HOME

                WORKDIR $AGENT_HOME

                CMD uvicorn planner_agent:app --reload --host 0.0.0.0 --port $AGENT_PORT

    ''')
    return template

def generate_main_file(app_dir, id_date):

    main_file = dedent(f"""
    import os
    import sys

    path = '/home/guess/Desktop/scanflow'
    sys.path.append(path)

    from scanflow.setup import setup
    from scanflow.run import run

    # App folder
    app_dir = '{app_dir}'

    # Workflows
    workflow1 = [
        {{'name': 'gathering-{id_date}', 'file': 'gathering.py',
                'env': 'gathering'}},

        {{'name': 'preprocessing-{id_date}', 'file': 'preprocessing.py',
                'env': 'preprocessing'}},

    ]
    workflow2 = [
        {{'name': 'modeling-{id_date}', 'file': 'modeling.py',
                'env': 'modeling'}},


    ]
    workflows = [
        {{'name': 'workflow1', 'workflow': workflow1, 'tracker': {{'port': 8001}}}},
        {{'name': 'workflow2', 'workflow': workflow2, 'tracker': {{'port': 8002}}}}

    ]

    workflow_datascience = setup.Setup(app_dir, workflows)


    # Read the platform
    runner = run.Run(workflow_datascience)

    # Run the workflow
    runner.run_workflows()

    """)

    return main_file


def create_registry(name='scanflow_registry'):
    """
    Build a environment with Docker images.

    Parameters:
        name (str): Prefix of a Docker image.
    Returns:
        image (object): Docker image.
    """
    port_ctn = 5000 # By default (inside the container)
    port_host = 5000 # Expose this port in the host
    ports = {f'{port_ctn}/tcp': port_host}

    # registry_image = 'registry' # Registry version 2 from Docker Hub
    registry_image = 'registry:latest' # Registry version 2 from Docker Hub
    restart = {"Name": "always"}

    try:
        container = client.containers.get(name)
        logging.info(f"[+] Registry: [{name}] exists in local.")

        # return {'name': name, 'ctn': container_from_env}
        return container

    except docker.api.client.DockerException as e:
        # logging.error(f"{e}")
        logging.info(f"[+] Registry: [{name}] is not running in local. Running a new one.")

    try:
        container = client.containers.run(image=registry_image,
                                          name=name,
                                          tty=True, detach=True,
                                          restart_policy=restart,
                                          ports=ports)

        logging.info(f'[+] Registry [{name}] was built successfully.')
        logging.info(f'[+] Registry [{name}] is running at port [{port_host}].')

        return container

    except docker.api.client.DockerException as e:
        logging.error(f"{e}")
        logging.error(f"[-] Registry creation failed.", exc_info=True)


def build_image(name, dockerfile_dir, dockerfile_path,
                node_type='executor', port=None, tracker_dir=None):

    image_from_repo = None

    try:
        image_from_repo = client.images.get(name)
        # environments.append({name: {'image': image_from_repo}})

    except docker.api.client.DockerException as e:
        # logging.error(f"{e}")
        logging.info(f"[+] Image [{name}] not found in repository. Building a new one.")
    try:

        if image_from_repo is None:
            image = client.images.build(path=dockerfile_dir,
                                        dockerfile=dockerfile_path,
                                        tag=name)
            # image = client.images.build(path=os.path.join(app_dir, 'workflow'),
            #                             dockerfile=dockerfile_path,
            #                             tag=name)
            logging.info(f'[+] Image [{name}] was built successfully.')
            # self.env_image = image[0]
            # environments.append({name: {'image': image[0]}})
            if node_type == 'tracker':
                metadata = {'name': name, 'image': image[0].tags,
                            'type': node_type, 'status': 0,
                            'port': port, 'tracker_dir': tracker_dir}  # 0:not running
            else:
                metadata = {'name': name, 'image': image[0].tags,
                            'type': node_type, 'status': 0} # 0:not running

            return metadata

        else:
            logging.warning(f'[+] Image [{name}] already exists.')
            logging.info(f'[+] Image [{name}] was loaded successfully.')

            if node_type == 'tracker':
                metadata = {'name': name, 'image': image_from_repo.tags,
                            'type': node_type, 'status': 0,
                            'port': port, 'url': f'http://localhost:{port}/',
                            'tracker_dir': tracker_dir}  # 0:not running
            else:
                metadata = {'name': name, 'image': image_from_repo.tags,
                            'type': node_type, 'status': 0} # 0:not running

            return metadata

            # return {'name': name, 'image': image_from_repo,
            #         'type': node_type, 'status': 0, 'port': port}

    except docker.api.client.DockerException as e:
        logging.error(f"{e}")
        logging.error(f"[-] Image building failed.", exc_info=True)

def build_image_to_registry(registry, name, dockerfile_dir, dockerfile_path,
                node_type='executor', port=None, tracker_dir=None):

    image_from_repo = None

    try:
        image_from_repo = client.images.get(name)

    except docker.api.client.DockerException as e:
        logging.info(f"[+] Image [{name}] not found in repository. Building a new one.")
    try:

        if image_from_repo is None:
            tag = f"{registry}/{name}"
            image = client.images.build(path=dockerfile_dir,
                                        dockerfile=dockerfile_path,
                                        tag=tag)
            logging.info(f'[+] Image [{name}] was built successfully.')
            client.images.push(tag)
            logging.info(f'[+] Image [{name}] was pushed to registry successfully.')
            if node_type == 'tracker':
                metadata = {'name': name, 'image': image[0].tags,
                            'type': node_type, 'status': 0,
                            'port': port, 'tracker_dir': tracker_dir}  # 0:not running
            else:
                metadata = {'name': name, 'image': image[0].tags,
                            'type': node_type, 'status': 0} # 0:not running
            return metadata

        else:
            logging.warning(f'[+] Image [{name}] already exists.')
            logging.info(f'[+] Image [{name}] was loaded successfully.')

            if node_type == 'tracker':
                metadata = {'name': name, 'image': image_from_repo.tags,
                            'type': node_type, 'status': 0,
                            'port': port, 'url': f'http://localhost:{port}/',
                            'tracker_dir': tracker_dir}  # 0:not running
            else:
                metadata = {'name': name, 'image': image_from_repo.tags,
                            'type': node_type, 'status': 0} # 0:not running

            return metadata

    except docker.api.client.DockerException as e:
        logging.error(f"{e}")
        logging.error(f"[-] Image building failed.", exc_info=True)

 
def start_image(image, name, network=None, **kwargs):

    container_from_env = None

    try:
        container_from_env = client.containers.get(name)

        if container_from_env.status == 'exited':
            container_from_env.stop()
            container_from_env.remove()
            container_from_env = None
        # return {'name': name, 'ctn': container_from_env}
        # return container_from_env

    except docker.api.client.DockerException as e:
        # logging.error(f"{e}")
        logging.info(f"[+] Environment: [{name}] has not been started in local. Starting a new one.")
    try:

        if container_from_env is None:  # does not exist in repo
            env_container = client.containers.run(image=image, name=name,
                                                  network=network,
                                                  tty=True, detach=True,
                                                  **kwargs)

            return env_container
        else:
            logging.warning(f'[+] Environment: [{name}] is already running.')
            # logging.info(f'[+] Image [{name}] was loaded successfully.')

    except docker.api.client.DockerException as e:
        logging.error(f"{e}")
        logging.error(f"[-] Starting environment: [{name}] failed.", exc_info=True)


def run_environment(name, network, volume=None, port=None, environment=None):

    container_from_env = None
    pass

def start_network(name):

    net_from_env = None

    try:
        net_from_env = client.networks.get(name)

    except docker.api.client.DockerException as e:
        # logging.error(f"{e}")
        logging.info(f"[+] Network: [{name}] has not been started in local. Starting a new one.")
    try:

        if net_from_env is None: # does not exist in repo
            net = client.networks.create(name=name)

            # logging.info(f'[+] Container [{name}] was built successfully.')
            logging.info(f'[+] Network: [{name}] was started successfully')
            # self.env_image = image[0]
            # environments.append({name: {'image': image[0]}})
            return net
        else:
            logging.warning(f'[+] Network: [{name}] is already running.')
            # logging.info(f'[+] Image [{name}] was loaded successfully.')

    except docker.api.client.DockerException as e:
        logging.error(f"{e}")
        logging.error(f"[-] Starting network: [{name}] failed.", exc_info=True)


def generate_data(path, file_system='local', **args):
    """
        n_samples=100,n_features=4,
        class_sep=1.0, n_informative=2,
        n_redundant=2, random_state=rs

        Example:
        generate_data(path='./raw_data.csv', file_system='local',
                  n_samples=10000, n_features=4,
                  class_sep=1.0, n_informative=2,
                  n_redundant=2, random_state=1)
    """

    X, y = make_classification(**args)

    df = pd.DataFrame(X, columns=['x_' + str(i + 1) for i in range(X.shape[1])])
    df = pd.concat([df, pd.DataFrame({'y': y})], axis=1)

    if file_system == 'local':
        df.to_csv(path, index=False)
        print(df.head())
        logging.info(f'Dataset was generated successfully and saved in {path} ')

    elif file_system == 'hdfs':
        from pyspark.sql import SparkSession

        cluster_manager = 'yarn'
        spark = SparkSession.builder \
            .master(cluster_manager) \
            .appName("myapp") \
            .config("spark.driver.allowMultipleContexts", "true") \
            .getOrCreate()

        spark_df = spark.createDataFrame(df)
        spark_df.show(5)
        spark_df.limit(10000).write.mode('overwrite').parquet(path)
        logging.info(f'Dataset was generated successfully and saved in hdfs://{path} ')


def generate_mlproject(folder, environment, wflow_name='workflow_app'):
    # workflow_path = os.path.join(folder, 'workflow')
    # list_dir_mlproject = os.listdir(workflow_path)
    # mlproject = [w for w in list_dir_mlproject if 'MLproject' in w]
    mlproject_path = os.path.join(folder, 'workflow', 'MLproject')
    # if len(mlproject) == 0:
    mlproject = mlproject_template(environment, wflow_name)
    # with open(mlproject_path, 'w') as f:
    #     f.writelines(mlproject)
    filename = f"{mlproject_path}_{environment['name']}"
    with open(filename, 'w') as f:
        yaml.dump(mlproject, f, default_flow_style=False)

    logging.info(f'[+] MLproject [{filename}] was created successfully.')
    # else:
    #     logging.info(f'[+] MLproject was found.')
    return mlproject_path


def mlproject_template(environment, wflow_name):

    mlproject = {'name': f"{wflow_name}_{environment['name']}",
                 'entry_points': {
                     'main': {'command': f"python {environment['file']}"}
                 }
                 }

    return mlproject


def format_parameters(params):
    list_params = list()
    for k, v in params.items():
        if isinstance(v, list):
            list_params.append(f"--{k} {' '.join(v)}")
        else:
            list_params.append(f"--{k} {v}")

    return ' '.join(list_params)


def check_verbosity(verbose):
    logger = logging.getLogger()
    if verbose:
        logger.disabled = False
    else:
        logger.disabled = True


def get_scanflow_paths(app_dir):
    # 1. save workflow defined by user
    workflow_dir = os.path.join(app_dir, 'workflow')
    # 2. start template agent inside, and user modify the agents
    agents_dir = os.path.join(app_dir, 'agents')
    tracker_dir = os.path.join(agents_dir, 'tracker')
    checker_dir = os.path.join(agents_dir, 'checker')
    improver_dir = os.path.join(agents_dir, 'improver')
    planner_dir = os.path.join(agents_dir, 'planner')
    # 3. meta data generated by scanflow(for example, workflow.json) 
    meta_dir = os.path.join(app_dir, 'meta')
    deploy_dir = os.path.join(meta_dir, 'deploy')#maybe generate app

    paths = {'app_dir': app_dir,
                'workflow_dir': workflow_dir,
                'agents_dir': agents_dir,
                'meta_dir': meta_dir,
                'tracker_dir': tracker_dir,
                'checker_dir': checker_dir,
                'improver_dir': improver_dir,
                'planner_dir': planner_dir,
                'deploy': deploy_dir}

    return paths


def predict(input_path, port=5001):
    """
    Use the API to predict with a given input .

    Parameters:
        input_path (str): Input sample path.
        port (int): Predictor's port
    Returns:
        response_json (dict): prediction.
    """
    url = f'http://localhost:{port}/invocations'

    try:
        input_df = pd.read_csv(input_path)
        start = time.time()
        input_data_json = {
            'columns': list(input_df.columns),
            'data': input_df.values.tolist()
        }
        response = requests.post(
            url=url, data=json.dumps(input_data_json),
            headers={"Content-type": "application/json; format=pandas-split"})
        response_json = json.loads(response.text)

        end = time.time()
        logging.info(f'Predicting from port: {port}')
        logging.info(f'Time elapsed: {end-start}')

        preds = [d for d in response_json]
        input_df['pred'] = preds

        return input_df

    except requests.exceptions.HTTPError as e:
        logging.error(f"{e}")
        logging.error(f"Request to API failed.")


def run_step(step):
    """
    Run a workflow that consists of several python files.

    Parameters:
        workflow (dict): Workflow of executions
    Returns:
        image (object): Docker image.
    """
    # logging.info(f'Running workflow: type={self.app_type} .')
    # logging.info(f'[+] Running workflow on [{env_container_name}].')
    try:
        env_name = step['name']
        env_container = client.containers.get(env_name)
        if 'parameters' in step.keys():
            cmd = f"python {step['file']} {format_parameters(step['parameters'])}"
            # result = env_container.exec_run(cmd=cmd,
            #                                 workdir='/app/workflow')
            # result = env_container.exec_run(cmd=cmd,
            #                                 workdir='/mlperf')
            result = env_container.exec_run(cmd=cmd,
                                            workdir='/app/workflow')
        else:
            result = env_container.exec_run(cmd=f"python {step['file']}",
                                            workdir='/app/workflow')

        # result = env_container.exec_run(cmd=f"python workflow/{self.workflow['main']}")
        logging.info(f"[+] Running ({step['file']}). ")
        logging.info(f"[+] Output:  {result.output.decode('utf-8')} ")

        logging.info(f"[+] Environment ({env_name}) finished successfully. ")

        # return env_container, result
        return env_name, result
        # self.logs_workflow = result.output.decode("utf-8")

    except docker.api.client.DockerException as e:
        logging.error(f"{e}")
        logging.error(f"[-] Environment [{step['name']}] has not started yet.")

    return None


def save_workflows(paths, workflows):
    meta_dir = paths['meta_dir']

    workflows_metadata_name = 'workflows.json'
    workflows_metadata_path = os.path.join(meta_dir, workflows_metadata_name)

    with open(workflows_metadata_path, 'w') as fout:
        json.dump(workflows, fout)


def read_workflows(paths):
    meta_dir = paths['meta_dir']

    workflows_metadata_name = 'workflows.json'
    workflows_metadata_path = os.path.join(meta_dir, workflows_metadata_name)

    try:
        with open(workflows_metadata_path) as fread:
            data = json.load(fread)

        return data

    except ValueError as e:
        logging.error(f"{e}")
        logging.error(f"[-] Workflows metadata has not yet saved.")


def workflow_to_graph(wflows_meta, name='Graph 1'):
    graph = list()
    last_nodes = list()
    if_tracker = 0
    for wflow in wflows_meta:
        # Parent nodes
        nodes = wflow['nodes']
        parent_node_name = wflow['name']
        # Root parent (e.g, Data science team)
        graph.append({'data': {'id': name,
                                   'label': name}})
        # Workflow parent (e.g, workflow1)
        graph.append({'data': {'id': parent_node_name,
                                   'label': parent_node_name,
                                   'parent': name}})

        if_tracker = int(any("tracker" in node['name'] for node in nodes))
        for i, node in enumerate(nodes):
            children_node_name = node['name']
            if node['type'] == 'executor':
                # Children nodes
                graph.append({'data': {'id': children_node_name,
                                           'label': children_node_name,
                                           'parent': parent_node_name}})
                # Edges in each workflow
                if i+1+if_tracker < len(nodes):
                    graph.append({'data': {'source': children_node_name,
                                               'target': nodes[i+1]['name']}})

                if i == len(nodes)-(1 + if_tracker):
                    last_nodes.append(children_node_name)

        if_tracker = 0

    # Edges between workflows
    for i, last_node in enumerate(last_nodes):
        if i+1 < len(last_nodes):
            graph.append({'data': {'source': last_node,
                                   'target': last_nodes[i+1]}})

    return graph


def draw_graph(graph):
    G = nx.DiGraph(directed=True)

    edges_with_parent = [(d['data']['parent'], d['data']['id'])
              for d in graph if 'parent' in d['data'].keys()]
    parent_nodes = {edge[0]:'blue' for edge in edges_with_parent}
    # color_map = ['blue' for e in edges]
    edges_rest = [(d['data']['source'], d['data']['target'])
              for d in graph if 'source' in d['data'].keys()]

    rest_nodes = {edge:'cyan' for edge in list(set(list(sum(edges_rest, ()))))}

    total_edges = edges_with_parent + edges_rest

    G.add_edges_from(total_edges)

#     plt.title('Topology')
    pos = nx.spectral_layout(G)
    color_nodes = {**parent_nodes, **rest_nodes}
    color_map = [color_nodes[node] for node in G.nodes()]
    fig = plt.figure()
    fig.add_subplot(1, 1, 1)
    plt.title("Workflow")
    nx.draw(G, pos, node_color=color_map, with_labels = True, arrows=True)
    plt.show()