import logging
import os
from typing import List

import scanflow.deployer.deployer as deployer
from scanflow.templates import SeldonClient, SeldonDeployments, SeldonPodSpec, PredictiveUnit, PredictorSpec
from scanflow.deployer.env import ScanflowSecret, ScanflowClientConfig
from scanflow.app import Workflow

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
        self.seldonDeployments = None
    
    # deploy application contains different version of models
    # this function is not ready now(14/11)
    def deploy_app(self, namespace, app, replicas: int = 1):
        """
           deploy application(diff version?) by seldon
        """
        #SeldonDeployments
        app_name = app.app_name
        annotations = {'seldon.io/istio-gateway':'mesh','seldon.io/istio-host':''}
        self.seldonDeployments = SeldonDeployments(app_name, namespace, replicas)
        #1. volume
        volumes = self.kubeclient.build_volumes(scanflowpath=f"scanflow-{namespace}")
        
        submitted = True
        for workflow in workflows:
            logging.info(f"[++] Deploying workflow: [{workflow.name}].")
            submitted = submitted and self.deploy_workflow(namespace, workflow, replicas)
            logging.info(f"[+] Workflow: [{workflow.name}] was deployed successfully.")
    
        #deploy
        logging.info(f"[+++] Workflow: deploying [{app_name}] to seldon {self.seldonDeployments.to_dict()}")
        return self.kubeclient.create_seldonDeployment(namespace, self.seldonDeployments.to_dict())

    def deploy_workflows(self, namespace, workflows, replicas: int = 1):
        submitted = True
        for workflow in workflows:
            logging.info(f"[++] Deploying workflow: [{workflow.name}].")
            submitted = submitted and self.deploy_workflow(namespace, workflow, replicas)
            logging.info(f"[+] Workflow: [{workflow.name}] was deployed successfully.")
        return submitted

    def deploy_workflow(self, namespace, workflow, replicas: int = 1, 
                        backupservice: dict = None):
        """
           deploy workflow by seldon
        """
        #if self.seldonDeployments is None:
        workflow_name = workflow.name
        self.seldonDeployments = SeldonDeployments(workflow_name, namespace, replicas)
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
                containers.append(self.kubeclient.build_container(service.name, 
                                 service.image, env=self.kubeclient.build_env(**env), 
                                 volume_mounts=self.kubeclient.build_volumeMounts(scanflowpath="/scanflow"),
                                 resources=service.resources))
            #predictiveUnit
            predictiveUnits[f"{service.name}"] = PredictiveUnit(service.name, 
                         type=service.service_type, implementation=service.implementation_type,
                         endpoint=service.endpoint, parameters=service.parameters, 
                         modelUri=service.modelUri, envSecretRefName=service.envSecretRefName)

        componentSpecs = None
        seldonPodSpec = SeldonPodSpec()
        if containers:
            spec = self.kubeclient.build_podSpec(containers, volumes=volumes)
            seldonPodSpec.spec = spec
        if workflow.kedaSpec:
            seldonPodSpec.kedaSpec = workflow.kedaSpec
        componentSpecs = [seldonPodSpec]

        #edges
        logging.info(f"[+] Building workflow: [{workflow_name}- edges]")
        if workflow.edges:
            edge_count = {}
            for edge in workflow.edges:
                edge_count[f"{edge.dependee}"] = 0
                edge_count[f"{edge.depender}"] = 0
            for edge in workflow.edges:
                edge_count[f"{edge.depender}"] = edge_count[f"{edge.depender}"] + 1
                predictiveUnits[f"{edge.dependee}"].add_children(predictiveUnits[f"{edge.depender}"])
        else:
            logging.info(f"[+] workflow does not have edges")
            

        
        #graph
        logging.info(f"[+] Building workflow: [{workflow_name}- graph]")
        if workflow.edges:
            graph_head = None
            for k,v in edge_count.items():
                if v == 0:
                    graph_head = k
            logging.info(f"Graph head: {graph_head}")
            predictor = PredictorSpec(workflow_name, predictiveUnits[f"{graph_head}"],
                                          componentSpecs, replicas, engineResources=workflow.resources)        
        else:
            predictor = PredictorSpec(workflow_name, predictiveUnits[f"{workflow.nodes[0].name}"],
                                            componentSpecs, replicas, engineResources=workflow.resources)   

        #traffic
        predictor.traffic = 100
        
        if backupservice is not None:
            backupPredictor = predictor
            backupPredictor.graph.modelUri = backupservice['modelUri']
            backupPredictor.name = "backup"
            backupPredictor.traffic = 0
            self.seldonDeployments.predictors = [predictor, backupPredictor] 
        else:
            self.seldonDeployments.predictors = [predictor]     

        #deploy
        logging.info(f"[+++] Workflow: deploying [{workflow_name}] to seldon {self.seldonDeployments.to_dict()}")
        return self.kubeclient.create_seldonDeployment(namespace, self.seldonDeployments.to_dict())


    def update_traffic(self,
                       namespace,
                       name,
                       body: dict):
        oldjson = self.kubeclient.get_virtualservice(namespace, name)
        oldjson["spec"]["http"][0]["route"] = body["route"]
        logging.info(f"[++++++++++++++++++++++++++]update traffic {oldjson}")
        return self.kubeclient.replace_virtualservice(namespace, name, oldjson)


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

    def delete_workflows(self,
                         namespace: str,
                         workflows: List[Workflow]):
        """
        delete seldon workflows
        """
        deleted = True
        for workflow in workflows:
            deleted = deleted and self.delete_workflow(namespace, workflow)
        return deleted

    def delete_workflow(self, 
                        namespace: str,
                        workflow: Workflow):
        
        workflow_name = workflow.name
        deleted = False
        try:
            result = self.kubeclient.delete_seldonDeployment(namespace, workflow_name)
            if result is not None:
                deleted = True
        except:
            logging.info(f"cannot find workflows")
        finally:
            #output dir
            #self.kubeclient.delete_persistentvolumeclaim(namespace, workflow_name)
            #self.kubeclient.delete_persistentvolume(workflow_name)
            return deleted

    