"""
abstract deployer class
"""
import logging

from typing import List
from scanflow.app import Application, Tracker, Workflow, Agent

from scanflow.templates import Kubernetes


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class Deployer():
    def __init__(self,
                 k8s_config_file=None):

        self.kubeclient = Kubernetes(k8s_config_file=k8s_config_file)


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

        #tempo mount scanflow
        step8 = self.__create_scanflow_volume(namespace)

        # 7. start_agent if has
        if agents is not None:
            step7 = self.start_agents(namespace, agents)
        else:
            step7 = True

        return  step1 and step2 and step3 and step4 and step5 and step6 and step7 and step8 

    def __create_scanflow_volume(self,namespace):
        #scanflow volume, we have to pack scanflow, now we mount the volume
        #name pv-scanflow-server "/gpfs/bsc_home/xpliu/pv/jupyterhubpeini"
        # logging.info(f"[TEMPO: Because we dont have scanflow pip install now, we need to mount scanflow]")
        # pv = self.kubeclient.build_persistentvolume(f"scanflow-{namespace}", "1Gi", "/home/rocky/k8s_resources")
        # step1 = self.kubeclient.create_persistentvolume(body=pv)
        
        # ln -s /home/rocky/k8s_resources/scanflow /nfsfileshare/scanflow-mnist-datascience-scanflow-scanflow-mnist-datascience-pvc-d0a4c05e-f710-416e-9d5e-fff12eac0f91/scanflow

        step1 = True
        pvc = self.kubeclient.build_persistentvolumeclaim(namespace, f"scanflow-{namespace}", None, "ReadWriteMany","1Gi")
        step2 = self.kubeclient.create_persistentvolumeclaim(namespace, pvc)
        return step1 and step2
    
    def __delete_scanflow_volume(self, namespace):
        step1 = self.kubeclient.delete_persistentvolumeclaim(namespace, f"scanflow-{namespace}")
        # step2 = self.kubeclient.delete_persistentvolume(f"scanflow-{namespace}")
        step2 = True
        return step1 and step2

    def clean_environment(self,
                          namespace: str,
                          agents: List[Agent] = None):
        """
           delete env and stop agents
        """
        # 1. delete agent
        if agents is not None:
            step1 = self.stop_agents(namespace, agents)
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
        
        # tempo
        step8 = self.__delete_scanflow_volume(namespace)

        return step1 and step2 and step3 and step4 and step5 and step6 and step7 and step8

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

    def start_agents(self, 
                     namespace: str,
                     agents: List[Agent]):
        """
          deploy agents
        """
        for agent in agents:
            self.start_agent(namespace, agent)

    def start_agent(self,
                    namespace: str,
                    agent: Agent):
        agent_name = agent.name
        #deployment
        env = self.kubeclient.build_env(NAMESPACE=namespace)
        env_from_list = self.kubeclient.build_env_from_source(
            secret_ref = "scanflow-secret",
            config_map_ref = "scanflow-client-env"
        )
        volumes = self.kubeclient.build_volumes(scanflowpath=f"scanflow-{namespace}")
        volumeMounts = self.kubeclient.build_volumeMounts(scanflowpath="/scanflow")
        deployment = self.kubeclient.build_deployment(namespace = namespace, 
        name = agent_name, 
        label = "agent", 
        image = agent.image,
        volumes = volumes,
        env_from = env_from_list,
        env=env,
        volumeMounts = volumeMounts)

        step1 = self.kubeclient.create_deployment(namespace, deployment)
        logging.info(f"[+] Created {agent_name} Deployment {step1}")

        #service
        ports= self.kubeclient.build_servicePort('TCP',port=80,targetPort=8080)
        service=self.kubeclient.build_service(namespace = namespace, 
        name = agent_name, 
        label = "agent", 
        ports = ports,
        type = "ClusterIP")

        step2 = self.kubeclient.create_service(namespace = namespace, body=service)
        logging.info(f"[+] Created {agent_name} Service {step2}")

        return step1 and step2

    def stop_agents(self, 
                    namespace: str, 
                    agents: List[Agent]):
        """
           stop agents
        """
        for agent in agents:
            self.stop_agent(namespace, agent)

    def stop_agent(self,
                   namespace: str,
                   agent: Agent):
        agent_name = agent.name
        logging.info(f"[++] Stopping agent: [{agent_name}].")
        step1 = self.kubeclient.delete_deployment(namespace, agent_name)
        step2 = self.kubeclient.delete_service(namespace, agent_name)
        return step1 and step2

    # workflows: with different deployer
    def run_workflows(self,
                      namespace: str,
                      workflows: List[Workflow]):
        """
           run batch workflow
        """
        raise NotImplementedError("Backend:run_workflows")

    def run_workflow(self,
                     namespace: str,
                     workflows: Workflow):
        raise NotImplementedError("Backend:run_workflow")

    def delete_workflows(self, 
                         namespace: str,
                         workflows: List[Workflow]):
        """
           delete batch workflow
        """
        raise NotImplementedError("Backend:delete_workflows")

    def delete_workflow(self,
                        namespace: str,
                        workflow: Workflow):
        raise NotImplementedError("Backend:delete_workflow")
    
    #online
    def deploy_workflows(self,
                         namespace: str,
                         workflows: List[Workflow],
                         replicas: int):
        raise NotImplementedError("Backend: deploy_workflows")

    def deploy_workflow(self,
                        namespace: str,
                        workflow: Workflow,
                        replicas: int):
        raise NotImplementedError("Backend: deploy_workflow")

    def update_workflows(self,
                         namespace: str,
                         workflows: List[Workflow]):
        raise NotImplementedError("Backend: update_workflows")

    def update_workflow(self,
                        namespace: str,
                        workflow: Workflow):
        raise NotImplementedError("Backend: update_workflow")

    
