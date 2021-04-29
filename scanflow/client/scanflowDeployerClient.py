import logging
import os

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool
from typing import List, Dict

# scanflow deployer
from scanflow.server.utils import (
    set_server_uri,
    is_server_uri_set,
    get_server_uri,
)
import requests
import json

from scanflow.tools.scanflowtools import check_verbosity
from scanflow.deployer.env import ScanflowClientConfig, ScanflowTrackerConfig, ScanflowSecret, ScanflowEnvironment
from scanflow.app import Application

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ScanflowDeployerClient:
    def __init__(self,
                 user_type: str = "local",
                 deployer: str = "argo",
                 k8s_config_file: str = None,
                 scanflow_server_uri: str = None,
                 verbose=True):
        """
            user_type: default(local):user uses local notebook, incluster user call in cluster scanflow server
            deployer: deploy backend to run workflows
                      for offline batch usually use 'argo'
                      for online inference usually use 'seldon'
            scanflow_server_uri
                      =http://scanflow-server-service.scanflow-system.svc.cluster.local
            k8s_config_file: if provide use it, if cannot found use in_cluster_config
        """
        self.verbose = verbose
        check_verbosity(verbose)

        self.deployer = deployer
        self.user_type = user_type
        if user_type == "incluster":
            if scanflow_server_uri is not None:
               set_server_uri(scanflow_server_uri)
            if not is_server_uri_set():
                raise ValueError("Scanflow_server_uri is not provided")
            self.scanflow_server_uri = get_server_uri()
        else: 
            #user_type == "local"
            self.deployerbackend = self.get_deployer(deployer, k8s_config_file)

### Scanflow local deploy backend
    def get_deployer(self, deployer, k8s_config_file):
        if deployer == "argo":
            from scanflow.deployer.argoDeployer import ArgoDeployer
            return ArgoDeployer(k8s_config_file)
        elif deployer == "volcano":
            from scanflow.deployer.volcanoDeployer import VolcanoDeployer
            return VolcanoDeployer(self.verbose)
        elif deployer == "seldon":
            from scanflow.deployer.seldonDeployer import SeldonDeployer
            return SeldonDeployer(self.verbose)
        else:
            raise ValueError("unknown deployer: " + deployer)

    def create_environment(self, 
                           app: Application,
                           scanflowEnv: ScanflowEnvironment=None):
        if self.user_type == "incluster":
            url = f"{self.scanflow_server_uri}/create_environment"
            json_data = {
                'app': app.to_dict(),
                'scanflowEnv': scanflowEnv.__dict__
            }
            response = requests.post(url=url,
            data= json.dumps(json_data),
            headers={"accept": "application/json"})

            if json.loads(response.text)['status'] == 0:
                return True
            else:
                logging.error(f"create scanflow application env error {response.text['status']}")
                return False

        else: #local
            if scanflowEnv is None:
                scanflowEnv = ScanflowEnvironment()
                namespace = f"scanflow-{app.app_name}-{app.team_name}" 
                scanflowEnv.namespace = namespace
                scanflowEnv.tracker_config.TRACKER_STORAGE = f"postgresql://scanflow:scanflow123@postgresql-service.postgresql.svc.cluster.local/{namespace}"
                scanflowEnv.tracker_config.TRACKER_ARTIFACT = f"s3://scanflow/{namespace}"
                scanflowEnv.client_config.SCANFLOW_TRACKER_LOCAL_URI = f"http://scanflow-tracker.{namespace}.svc.cluster.local"

            result = self.deployerbackend.create_environment(scanflowEnv.namespace, scanflowEnv.secret.__dict__, scanflowEnv.tracker_config.__dict__, scanflowEnv.client_config.__dict__, app.tracker, app.agents)
            return result


    def clean_environment(self, 
                          app: Application):
        if self.user_type == "incluster":
            url = f"{self.scanflow_server_uri}/clean_environment"
            response = requests.post(url=url,
            data= json.dumps(app.to_dict()),
            headers={"accept": "application/json"})

            if json.loads(response.text)['status'] == 0:
                return True
            else:
                logging.error(f"clean scanflow application env error {response.text['status']}")
                return False

        else: #local
            namespace = f"scanflow-{app.app_name}-{app.team_name}" 
            result = self.deployerbackend.clean_environment(namespace)
            return result

    def run_workflows(self,)

