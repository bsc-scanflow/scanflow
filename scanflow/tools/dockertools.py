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
