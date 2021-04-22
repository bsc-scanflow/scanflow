import logging
import os

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool
from typing import List, Dict

from scanflow.app import Application

# scanflow deployer
from scanflow.server.utils import (
    set_server_uri,
    is_server_uri_set,
    get_server_uri,
)
import requests
import json

from scanflow.tools.scanflowtools import check_verbosity


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ScanflowDeployerClient:
    def __init__(self,
                 user_type="local",
                 deployer="argo",
                 k8s_config_file=None,
                 scanflow_server_uri=None,
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
            return ArgoDeployer(k8s_config_file, self.verbose)
        elif deployer == "volcano":
            from scanflow.deployer.volcanoDeployer import VolcanoDeployer
            return VolcanoDeployer(self.verbose)
        elif deployer == "seldon":
            from scanflow.deployer.seldonDeployer import SeldonDeployer
            return SeldonDeployer(self.verbose)
        else:
            raise ValueError("unknown deployer: " + deployer)

    def create_environment(self, 
                           app: Application = None):
        if app is not None:
            if self.user_type == "server":
                url = f"http://{self.scanflow_server_uri}/create_environment"

            else: #local
                self.deployerbackend.create_environment(app)
        else:
            raise ValueError("must provide scanflow application")

    def clean_environment(self, app: Application):
        print("")

