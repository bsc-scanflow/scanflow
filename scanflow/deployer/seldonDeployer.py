import logging
import os
from typing import List

import scanflow.deployer.deployer as deployer
from scanflow.templates import SeldonClient, SeldonDeployments, ComponentSpec, PredictiveUnit
from scanflow.deployer.env import ScanflowSecret, ScanflowClientConfig

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

    def deploy_workflows(self, namespace, workflows, replica: int = 1):
        submitted = True
        for workflow in workflows:
            logging.info(f"[++] Deploying workflow: [{workflow.name}].")
            submitted = submitted and self.deploy_workflow(namespace, workflow, replica)
            logging.info(f"[+] Workflow: [{workflow.name}] was deployed successfully.")
        return submitted

    def deploy_workflow(self, namespace, workflow, replica: int = 1):
        """
           deploy workflow by seldon
        """
        workflow_name = workflow.name
        self.seldonDeployments = SeldonDeployments(workflow_name, namespace, replica)
     
        #volume
        volumes = self.kubeclient.build_volumes(scanflowpath=f"scanflow-{namespace}")
        #env
        ss = ScanflowSecret()
        scc = ScanflowClientConfig()
        scc.SCANFLOW_TRACKER_LOCAL_URI = f"http://scanflow-tracker.{namespace}.svc.cluster.local"
        env = ss.__dict__
        env.update(scc.__dict__)
        logging.info(f"env for executor {env}")

        #services
        logging.info(f"[+] Building workflow: [{workflow_name}- service]")
        containers = []
        predictiveUnits = {}
        for service in workflow.nodes:
            #containers
            if service.service_type:
                if service.env is not None:
                    env.update(service.env)
                containers.append(self.kubeclient.build_container(service.name, service.image, env=self.kubeclient.build_env(**env), volume_mounts=self.kubeclient.build_volumeMounts(scanflowpath="/scanflow")))
            #predictiveUnit
            predictiveUnits[f"{service.name}"] = PredictiveUnit(service.name, type=service.service_type, implementation=service.implementation_type, endpoint=service.endpoint, parameters=service.parameters, modelUri=service.modelUri, envSecretRefName=service.envSecretRefName)

        if containers:
            spec = self.kubeclient.build_podSpec(containers, volumes=volumes)
            componentSpec = ComponentSpec(spec.to_dict())
            self.seldonDeployments.componentSpecs = [componentSpec.__dict__]

        #edges
        logging.info(f"[+] Building workflow: [{workflow_name}- edges]")
        if workflow.edges:
            edge_count = {}
            for edge in workflow.edges:
                edge_count[f"edge.dependee"] = 0
                edge_count[f"edge.depender"] = 0
            for edge in workflow.edges:
                edge_count[f"edge.depender"] = edge_count[f"edge.depender"] + 1
                predictiveUnits[f"{edge.dependee}"].add_children(predictiveUnits[f"{edge.depender}"])
        else:
            logging.info(f"[+] workflow does not have edges]")
            
        #graph
        logging.info(f"[+] Building workflow: [{workflow_name}- graph]")
        if workflow.edges:
            graph_head = None
            for k,v in edge_count.items():
                if v == 0:
                    graph_head = k
            self.seldonDeployments.graph = predictiveUnits[f"{graph_head}"].to_dict()           
        else:
            self.seldonDeployments.graph = predictiveUnits[f"{workflow.nodes[0].name}"].to_dict() 

        #deploy
        logging.info(f"[+++] Workflow: deploying [{workflow_name}] to seldon {self.seldonDeployments.to_dict()}")
        return self.kubeclient.create_seldonDeployment(namespace, self.seldonDeployments.to_dict())

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

    