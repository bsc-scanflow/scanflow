import logging
import os
from typing import List

#from scanflow.app import Workflow, Executor

import scanflow.deployer.deployer as deployer
from scanflow.templates import SeldonClient

#from scanflow.deployer.env import ScanflowSecret, ScanflowClientConfig
#from scanflow.tools.param import format_parameter

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

from scanflow.deployer.utils import (
    get_output_dir,
    set_output_dir,
    is_output_dir_set,
)

class SeldonDeployer(deployer.Deployer):
    def __init__(self,
                 k8s_config_file=True):
        super(SeldonDeployer, self).__init__(k8s_config_file)

        self.seldonClient = None

    def deploy_workflows(self, namespace, workflows):
        submitted = True
        for workflow in workflows:
            logging.info(f"[++] Deploying workflow: [{workflow.name}].")
            submitted = submitted and self.deploy_workflow(namespace, workflow)
            logging.info(f"[+] Workflow: [{workflow.name}] was deployed successfully.")
        return submitted

    def deploy_workflow(self, namespace, workflow):
        """
           deploy workflow by seldon
        """
        pass

    ## user can directly use seldonclient to develop their application, here we only wrapped seldon client
    #channel_credentials: SeldonChannelCredentials = None,
    #call_credentials: SeldonCallCredentials = None,
    def create_seldonClient(self,
                            gateway: str = "istio",
                            transport: str = "rest",
                            namespace: str = None,
                            deployment_name: str = None,
                            payload_type: str = "tensor",
                            gateway_endpoint: str = "localhost:8003",
                            microservice_endpoint: str = "localhost:5000",
                            grpc_max_send_message_length: int = 4 * 1024 * 1024,
                            grpc_max_receive_message_length: int = 4 * 1024 * 1024,
                            channel_credentials = None,
                            call_credentials = None,
                            debug: bool = False,
                            client_return_type: str = "dict",
                            ssl: bool = None):
        if self.seldonClient is None:
            self.seldonClient = SeldonClient(gateway,transport,namespace,deployment_name,payload_type,gateway_endpoint,microservice_endpoint,grpc_max_send_message_length, grpc_max_receive_message_length, channel_credentials, call_credentials, debug, client_return_type, ssl)

    def run_workflow(self, data):
        if self.seldonClient is None:
            raise NotImplementedError("seldonClient is not defined")
        else:
            return self.seldonClient.predict(data)

    