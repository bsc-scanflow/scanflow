"""
abstract deployer class
"""
import logging

from typing import List
from scanflow.app import Application, Tracker
from scanflow.agent import Agent

from scanflow.tools.scanflowtools import get_scanflow_paths, check_verbosity
from scanflow.templates import Kubernetes


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class Deployer():
    def __init__(self,
                 k8s_config_file=None,
                 verbose=True):
        self.verbose = verbose
        check_verbosity(verbose)

        self.kubeclient = Kubernetes(k8s_config_file=k8s_config_file, 
        verbose = verbose)


    def create_environment(self, 
                           namespace: str, 
                           scanflowSecret: dict,
                           scanflowTrackerConfig: dict,
                           scanflowClientConfig: dict,
                           tracker : Tracker = None,
                           agents: List[Agent] = None):
        """
          create namespace, role, agents...
        """
        logging.info(f'[++]Creating env')
        # 1. create namespace
        step1 = self.__create_namespace(namespace)
        # 2. create role
        step2 = self.__create_role(namespace)
        # 3. create secret 
        step3 = self.__create_secret(namespace, scanflowSecret)
        # 4. create tracker configmap
        step4 = self.__create_configmap_tracker(namespace, scanflowTrackerConfig)
        # 5. create client configmap
        step5 = self.__create_configmap_client(namespace, scanflowClientConfig)
        # 6. start local tracker 
        step6 = self.__start_local_tracker(namespace, tracker)
        # 7. start_agent if has
        if agents is not None:
            step7 = self.start_agents()
        else:
            step7 = True

        return  step1 and step2 and step3 and step4 and step5 and step6 and step7 

    def clean_environment(self,
                          namespace: str,
                          agents: List[Agent] = None):
        """
           delete env and stop agents
        """
        # 1. delete agent
        if agents is not None:
            step1 = self.stop_agents()
        else:
            step1 = True
        # 2. delete local_tracker
        step2 = self.__stop_local_tracker(namespace)
        # 3. delete others
        step3 = self.__delete_configmap_tracker(namespace) 
        step4 = self.__delete_configmap_client(namespace) 
        step5 = self.__delete_secret(namespace) 
        step6 = self.__delete_role(namespace) 
        # 4. delete namespace
        step7 = self.__delete_namespace(namespace)
        
        return step1 and step2 and step3 and step4 and step5 and step6 and step7

    def __create_namespace(self, namespace):
        logging.info(f'[++]Creating namespace "{namespace}"')
        return self.kubeclient.create_namespace(namespace)

    def __delete_namespace(self, namespace):
        logging.info(f'[++]Delete namespace "{namespace}"')
        return self.kubeclient.delete_namespace(namespace)

    def __create_role(self, namespace):
        logging.info(f"[++]Creating Role for 'default service account'")
        rolebinding = self.kubeclient.build_rolebinding(namespace)
        return self.kubeclient.create_rolebinding(namespace, rolebinding)

    def __delete_role(self, namespace):
        logging.info(f'[++]Delete rolebinding default-admin')
        return self.kubeclient.delete_rolebinding(namespace)

    def __create_secret(self, namespace, stringData):
        logging.info(f"[++]Creating s3 secret {stringData}")
        secret = self.kubeclient.build_secret("scanflow-secret",namespace, stringData)
        return self.kubeclient.create_secret(namespace, secret)

    def __delete_secret(self, namespace):
        logging.info(f'[++]Delete s3 secret scanflow-secret')
        return self.kubeclient.delete_secret(namespace, "scanflow-secret")

    def __create_configmap_tracker(self, namespace, data):
        logging.info(f"[++]Creating tracker configmap {data}")
        configmap = self.kubeclient.build_configmap("scanflow-tracker-env", namespace, data)
        return self.kubeclient.create_configmap(namespace,configmap)

    def __delete_configmap_tracker(self, namespace):
        logging.info(f'[++]Delete tracker configmap scanflow-tracker-env')
        return self.kubeclient.delete_configmap(namespace,"scanflow-tracker-env")
        
    def __create_configmap_client(self, namespace, data):
        logging.info(f"[++]Creating client configmap {data}")
        configmap = self.kubeclient.build_configmap("scanflow-client-env", namespace, data)
        return self.kubeclient.create_configmap(namespace,configmap)

    def __delete_configmap_client(self, namespace):
        logging.info(f'[++]Delete client configmap scanflow-client-env')
        return self.kubeclient.delete_configmap(namespace,"scanflow-client-env")



    def __start_local_tracker(self, namespace, tracker):
        """
          deploy tracker in namespaced env
        """
        tracker_name = "scanflow-tracker"
        logging.info(f"[+] Starting local tracker: [{tracker_name}].")
        # deployment
        env_from_list = self.kubeclient.build_env_from_source(
            secret_ref = "scanflow-secret",
            config_map_ref = "scanflow-tracker-env"
        )
        deployment = self.kubeclient.build_deployment(namespace = namespace, 
        name = tracker_name, 
        label = "scanflow", 
        image = tracker.image,
        env_from = env_from_list)

        step1 = self.kubeclient.create_deployment(namespace, deployment)
        logging.info(f"[+] Created tracker Deployment {step1}")

        #service
        ports= self.kubeclient.build_servicePort('TCP',port=80,targetPort=5000, nodePort=tracker.nodePort)
        service=self.kubeclient.build_service(namespace = namespace, 
        name = tracker_name, 
        label = "scanflow", 
        ports = ports,
        type = "NodePort")
        step2 = self.kubeclient.create_service(namespace = namespace, body=service)
        logging.info(f"[+] Created tracker Service {step2}")

        return step1 and step2

    def __stop_local_tracker(self, namespace):
        """
          stop local_tracker
        """
        tracker_name = "scanflow-tracker"
        logging.info(f"[++] Stopping tracker: [{tracker_name}].")
        step1 = self.kubeclient.delete_deployment(namespace, tracker_name)
        step2 = self.kubeclient.delete_service(namespace, tracker_name)
        return step1 and step2

    #agents

    def start_agents(self):
        """
          deploy agents
        """
        return True

    def stop_agents(self):
        """
           stop agents
        """
        return True




    # workflows: with different deployer

    def run_workflows(self):
        """
           run batch workflow
        """
        raise NotImplementedError("Backend:run_workflows")

    def delete_workflows(self):
        """
           delete batch workflow
        """
        raise NotImplementedError("Backend:delete_workflows")

    
