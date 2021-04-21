import logging
import subprocess
import os
import docker
import requests
import datetime

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool

import scanflow.deployer.deployer as deployer
from scanflow.templates import ArgoWorkflows

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)



class ArgoDeployer(deployer.Deployer):
    def __init__(self,
                 scanflowType=None,
                 verbose=True):
        super(ArgoDeployer, self).__init__(scanflowType, verbose)

        self.argoclient = ArgoWorkflows()
 
    def start_agents(self):

        if self.workflows_user is not None:
            for wflow_user in self.workflows_user:
                logging.info(f"[++] Starting workflow agents: [{wflow_user['name']}].")
                self.__start_agent(wflow_user)
                logging.info(f"[+] Workflow Agents: [{wflow_user['name']}] agents were started successfully.")
        else:
            raise ValueError('You must provide a workflow.')       
    
    def __start_agent(self, workflow):

        if 'tracker' in workflow.keys():

            tracker_name = f"tracker-{workflow['name']}"
            logging.info(f"[+] Starting tracker: [{tracker_name}].")

            workflow_tracker_dir = os.path.join(self.paths['ad_tracker_dir'], f"tracker-{workflow['name']}" )
            os.makedirs(workflow_tracker_dir, exist_ok=True)

            logging.info(f"[+] Create tracker PV")
            pv = self.kubeclient.build_persistentvolume(tracker_name, "2Gi", workflow_tracker_dir)
            self.kubeclient.create_persistentvolume(persistentvolume=pv)

            logging.info(f"[+] Create tracker PVC")
            pvc = self.kubeclient.build_persistentvolumeclaim(self.namespace, tracker_name, "2Gi")
            self.kubeclient.create_persistentvolumeclaim(self.namespace, pvc)

            logging.info(f"[+] Create tracker Deployment")
            volumes=self.kubeclient.build_volumes(mlflowpath=tracker_name)
            volumeMount=self.kubeclient.build_volumeMount(mlflowpath='/mlflow')
            env = self.kubeclient.build_env(
                MLFLOW_TRACKING_URI=f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
            )
            image = f"{self.registry}/{tracker_name}"
            deployment = self.kubeclient.build_deployment(self.namespace, tracker_name, 'scanflow', image, volumes, env, volumeMount)
            self.kubeclient.create_deployment(self.namespace, deployment=deployment)

            logging.info(f"[+] Create tracker Service")
            port = workflow['tracker']['port']
            ports= self.kubeclient.build_servicePort('TCP',port=port,targetPort=port, nodePort=30599)
            service=self.kubeclient.build_service(self.namespace, tracker_name, 'scanflow', ports, 'NodePort')
            self.kubeclient.create_service(self.namespace, service=service)

            if workflow['tracker']['mode'] == 'online':
                tracker_agent_name = f"tracker-agent-{workflow['name']}"
                logging.info(f"[+] Starting tracker agent: [{tracker_agent_name}].")

                workflow_tracker_dir_agent = os.path.join(workflow_tracker_dir, "agent")

                logging.info(f"[+] Create tracker agent PV")
                pv = self.kubeclient.build_persistentvolume(tracker_agent_name, "512Mi",workflow_tracker_dir_agent)
                self.kubeclient.create_persistentvolume(persistentvolume=pv)

                logging.info(f"[+] Create tracker agent PVC")
                pvc = self.kubeclient.build_persistentvolumeclaim(self.namespace, tracker_agent_name,"512Mi")
                self.kubeclient.create_persistentvolumeclaim(self.namespace, pvc)

                logging.info(f"[+] Create tracker agent Service")
                port_agent = workflow['tracker']['port'] + 1
                ports= self.kubeclient.build_servicePort('TCP',port=port_agent,targetPort=port_agent)
                service=self.kubeclient.build_service(self.namespace, tracker_agent_name, 'scanflow', ports, 'ClusterIP')
                self.kubeclient.create_service(self.namespace, service=service)

                logging.info(f"[+] Create tracker Deployment")
                volumes=self.kubeclient.build_volumes(agentpath=tracker_agent_name, mlflowpath=tracker_name)
                volumeMount=self.kubeclient.build_volumeMount(agentpath='/tracker/agent', mlflowpath='/mlflow')
                env = self.kubeclient.build_env(
                    AGENT_PORT=f"{port_agent}",
                    MLFLOW_TRACKING_URI=f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
                )
                image = f"{self.registry}/{tracker_agent_name}"
                deployment = self.kubeclient.build_deployment(self.namespace, tracker_agent_name, 'scanflow', image, volumes, env, volumeMount)
                self.kubeclient.create_deployment(self.namespace, deployment=deployment)

        if 'checker' in workflow.keys():
            checker_name = f"checker-{workflow['name']}"
            logging.info(f"[+] Starting checker: [{checker_name}].")

            workflow_checker_dir = self.paths['ad_checker_dir']
            os.makedirs(workflow_checker_dir, exist_ok=True)

#            logging.info(f"[+] Create checker PV")
#            pv = self.kubeclient.build_persistentvolume(checker_name,"1Gi", workflow_checker_dir)
#            self.kubeclient.create_persistentvolume(persistentvolume=pv)
#
#            logging.info(f"[+] Create checker PVC")
#            pvc = self.kubeclient.build_persistentvolumeclaim(self.namespace, checker_name, "1Gi")
#            self.kubeclient.create_persistentvolumeclaim(self.namespace, pvc)
#
#            logging.info(f"[+] Create checker Deployment")
#            volumes=self.kubeclient.build_volumes(checkerpath=checker_name, mlflowpath=tracker_name)
#            volumeMount=self.kubeclient.build_volumeMount(checkerpath='/checker', mlflowpath='/mlflow')
#            env = self.kubeclient.build_env(MLFLOW_TRACKING_URI=f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}")
#            image = f"{self.registry}/{checker_name}"
#            deployment = self.kubeclient.build_deployment(self.namespace, checker_name, 'scanflow', image, volumes, env, volumeMount)
#            self.kubeclient.create_deployment(self.namespace, deployment=deployment)
#
#            logging.info(f"[+] Create checker Service")
#            port = workflow['checker']['port']
#            ports= self.kubeclient.build_servicePort('TCP',port=port,targetPort=port, nodePort=30599)
#            service=self.kubeclient.build_service(self.namespace, tracker_name, 'scanflow', ports, 'NodePort')
#            self.kubeclient.create_service(self.namespace, service=service)


            if workflow['checker']['mode'] == 'online':
                checker_agent_name = f"checker-agent-{workflow['name']}"
                logging.info(f"[+] Starting checker agent: [{checker_agent_name}].")

                workflow_checker_dir_agent = os.path.join(workflow_checker_dir, "agent")

                logging.info(f"[+] Create checker agent PV")
                pv = self.kubeclient.build_persistentvolume(checker_agent_name, "512Mi", workflow_checker_dir_agent)
                self.kubeclient.create_persistentvolume(persistentvolume=pv)

                logging.info(f"[+] Create checker agent PVC")
                pvc = self.kubeclient.build_persistentvolumeclaim(self.namespace, checker_agent_name, "512Mi")
                self.kubeclient.create_persistentvolumeclaim(self.namespace, pvc)

                logging.info(f"[+] Create checker agent Service")
                port_agent = workflow['checker']['port'] + 1
                ports= self.kubeclient.build_servicePort('TCP',port=port_agent,targetPort=port_agent)
                service=self.kubeclient.build_service(self.namespace, checker_agent_name, 'scanflow', ports, 'ClusterIP')
                self.kubeclient.create_service(self.namespace, service=service)


                logging.info(f"[+] Create checker agent Deployment")
                volumes=self.kubeclient.build_volumes(agentpath=checker_agent_name, mlflowpath=tracker_name)
                volumeMount=self.kubeclient.build_volumeMount(agentpath='/checker/agent', mlflowpath='/mlflow')
                env = self.kubeclient.build_env(
                    AGENT_PORT=f"{port_agent}",
                    MLFLOW_TRACKING_URI=f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
                )
                image = f"{self.registry}/{checker_agent_name}"
                deployment = self.kubeclient.build_deployment(self.namespace, checker_agent_name, 'scanflow', image, volumes, env, volumeMount)
                self.kubeclient.create_deployment(self.namespace, deployment=deployment)


        if 'improver' in workflow.keys():
            workflow_improver_dir = self.paths['improver_dir']
            os.makedirs(workflow_improver_dir, exist_ok=True)

            if workflow['improver']['mode'] == 'online':
                improver_agent_name = f"improver-agent-{workflow['name']}"
                logging.info(f"[+] Starting improver agent: [{improver_agent_name}].")

                workflow_improver_dir_agent = os.path.join(workflow_improver_dir, "agent" )

                logging.info(f"[+] Create improver agent PV")
                pv = self.kubeclient.build_persistentvolume(improver_agent_name, "512Mi",workflow_improver_dir_agent)
                self.kubeclient.create_persistentvolume(persistentvolume=pv)

                logging.info(f"[+] Create improver agent PVC")
                pvc = self.kubeclient.build_persistentvolumeclaim(self.namespace, improver_agent_name, "512Mi")
                self.kubeclient.create_persistentvolumeclaim(self.namespace, pvc)

                logging.info(f"[+] Create improver agent Service")
                port_agent = workflow['improver']['port']
                ports= self.kubeclient.build_servicePort('TCP',port=port_agent,targetPort=port_agent)
                service=self.kubeclient.build_service(self.namespace, improver_agent_name, 'scanflow', ports, 'ClusterIP')
                self.kubeclient.create_service(self.namespace, service=service)


                logging.info(f"[+] Create improver agent Deployment")
                volumes=self.kubeclient.build_volumes(agentpath=improver_agent_name, mlflowpath=tracker_name)
                volumeMount=self.kubeclient.build_volumeMount(agentpath='/improver/agent', mlflowpath='/mlflow')
                env = self.kubeclient.build_env(
                    AGENT_PORT=f"{port_agent}",
                    MLFLOW_TRACKING_URI=f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
                )
                image = f"{self.registry}/{improver_agent_name}"
                deployment = self.kubeclient.build_deployment(self.namespace, improver_agent_name, 'scanflow', image, volumes, env, volumeMount)
                self.kubeclient.create_deployment(self.namespace, deployment=deployment)


        if 'planner' in workflow.keys():
            workflow_planner_dir = self.paths['planner_dir']
            os.makedirs(workflow_planner_dir, exist_ok=True)

            if workflow['planner']['mode'] == 'online':
                planner_agent_name = f"planner-agent-{workflow['name']}"
                logging.info(f"[+] Starting planner agent: [{planner_agent_name}].")

                workflow_planner_dir_agent = os.path.join(workflow_planner_dir, "agent" )

                logging.info(f"[+] Create planner agent PV")
                pv = self.kubeclient.build_persistentvolume(planner_agent_name, "512Mi", workflow_planner_dir_agent)
                self.kubeclient.create_persistentvolume(persistentvolume=pv)

                logging.info(f"[+] Create planner agent PVC")
                pvc = self.kubeclient.build_persistentvolumeclaim(self.namespace, planner_agent_name,"512Mi")
                self.kubeclient.create_persistentvolumeclaim(self.namespace, pvc)

                logging.info(f"[+] Create planner agent Service")
                port_agent = workflow['planner']['port']
                ports= self.kubeclient.build_servicePort('TCP',port=port_agent,targetPort=port_agent)
                service=self.kubeclient.build_service(self.namespace, planner_agent_name, 'scanflow', ports, 'ClusterIP')
                self.kubeclient.create_service(self.namespace, service=service)


                logging.info(f"[+] Create planner agent Deployment")
                volumes=self.kubeclient.build_volumes(agentpath=planner_agent_name, mlflowpath=tracker_name)
                volumeMount=self.kubeclient.build_volumeMount(agentpath='/planner/agent', mlflowpath='/mlflow')
                env = self.kubeclient.build_env(
                    AGENT_PORT=f"{port_agent}",
                    MLFLOW_TRACKING_URI=f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}"
                )
                image = f"{self.registry}/{planner_agent_name}"
                deployment = self.kubeclient.build_deployment(self.namespace, planner_agent_name, 'scanflow', image, volumes, env, volumeMount)
                self.kubeclient.create_deployment(self.namespace, deployment=deployment)


    def run_workflows(self):

        for wf_user in self.workflows_user:
            logging.info(f"[++] Running workflow: [{wf_user['name']}].")
            self.__run_workflow(wf_user)
            logging.info(f"[+] Workflow: [{wf_user['name']}] was run successfully.")

    def __run_workflow(self, workflow):
        """
        run workflow by argo
        """
        workflow_dir = self.paths['workflow_dir']
        workflow_name = f"{workflow['name']}"
        tracker_name = f"tracker-{workflow['name']}"

        logging.info(f"[+] Create {workflow_name} PV")
        pv = self.kubeclient.build_persistentvolume(workflow_name, "512Mi", workflow_dir)
        self.kubeclient.create_persistentvolume(persistentvolume=pv)

        logging.info(f"[+] Create {workflow_name} PVC")
        pvc = self.kubeclient.build_persistentvolumeclaim(self.namespace, workflow_name, "512Mi")
        self.kubeclient.create_persistentvolumeclaim(self.namespace, pvc)

        self.argoclient.buildVolumes(apppath=workflow_name, mlflowpath=tracker_name)


        env = { "MLFLOW_TRACKING_URI" : f"http://tracker-{workflow['name']}:{workflow['tracker']['port']}" }
        volumeMounts = self.argoclient.buildVolumeMounts(apppath='/app', mlflowpath='/mlflow')

        dependencies = None
        for task in workflow['executors']:
            logging.info(f"[+] Running workflow: [{workflow['name']}:{task['name']}].")

            image = f"{self.registry}/{task['name']}"
            self.argoclient.buildDagTask(f"{task['name']}", image, env, volumeMounts, dependencies)
            dependencies = [f"{task['name']}"]
         
        self.argoclient.submitWorkflow(self.namespace)


    def delete_workflows(self):
        """
        delete argo workflows
        """

    def stop_agents(self, tracker=True, checker=True,
                       improver=True, planner=True):
        """
        stop agents
        """
        if self.workflows_user is not None:
            for wflow_user in self.workflows_user:
                logging.info(f"[++] Stopping workflow agents: [{wflow_user['name']}].")
                if checker:
                    if 'checker' in wflow_user.keys():
                        checker_name=f"checker-{wflow_user['name']}"
                        logging.info(f"[++] Stopping checker: [{checker_name}].")
                        self.kubeclient.delete_deployment(self.namespace, checker_name)
                        self.kubeclient.delete_service(self.namespace, checker_name)
                        self.kubeclient.delete_persistentvolumeclaim(self.namespace, checker_name)
                        self.kubeclient.delete_persistentvolume(checker_name)
                        if wflow_user['checker']['mode'] == 'online':
                            checker_agent_name = f"checker-agent-{wflow_user['name']}"
                            logging.info(f"[++] Stopping checker agent: [{checker_agent_name}].")
                            self.kubeclient.delete_deployment(self.namespace, checker_agent_name)
                            self.kubeclient.delete_service(self.namespace, checker_agent_name)
                            self.kubeclient.delete_persistentvolumeclaim(self.namespace, checker_agent_name)
                            self.kubeclient.delete_persistentvolume(checker_agent_name)
                if improver:
                    if 'improver' in wflow_user.keys():
                        if wflow_user['improver']['mode'] == 'online':
                            improver_agent_name=f"improver-agent-{wflow_user['name']}"
                            logging.info(f"[++] Stopping improver agent: [{improver_agent_name}].")
                            self.kubeclient.delete_deployment(self.namespace, improver_agent_name)
                            self.kubeclient.delete_service(self.namespace, improver_agent_name)
                            self.kubeclient.delete_persistentvolumeclaim(self.namespace, improver_agent_name)
                            self.kubeclient.delete_persistentvolume(improver_agent_name)
                if planner:
                    if 'planner' in wflow_user.keys():
                        if wflow_user['planner']['mode'] == 'online':
                            planner_agent_name=f"planner-agent-{wflow_user['name']}"
                            logging.info(f"[++] Stopping planner agent: [{planner_agent_name}].")
                            self.kubeclient.delete_deployment(self.namespace, planner_agent_name)
                            self.kubeclient.delete_service(self.namespace, planner_agent_name)
                            self.kubeclient.delete_persistentvolumeclaim(self.namespace, planner_agent_name)
                            self.kubeclient.delete_persistentvolume(planner_agent_name)
                if tracker:
                    if 'tracker' in wflow_user.keys():
                        if wflow_user['tracker']['mode'] == 'online':
                            tracker_agent_name = f"tracker-agent-{wflow_user['name']}"
                            logging.info(f"[++] Stopping tracker agent: [{tracker_agent_name}].")
                            self.kubeclient.delete_deployment(self.namespace, tracker_agent_name)
                            self.kubeclient.delete_service(self.namespace, tracker_agent_name)
                            self.kubeclient.delete_persistentvolumeclaim(self.namespace, tracker_agent_name)
                            self.kubeclient.delete_persistentvolume(tracker_agent_name)
                        tracker_name=f"tracker-{wflow_user['name']}"
                        logging.info(f"[++] Stopping tracker: [{tracker_name}].")
                        self.kubeclient.delete_deployment(self.namespace, tracker_name)
                        self.kubeclient.delete_service(self.namespace, tracker_name)
                        self.kubeclient.delete_persistentvolumeclaim(self.namespace, tracker_name)
                        self.kubeclient.delete_persistentvolume(tracker_name)
 
                logging.info(f"[+] Workflow Agents: [{wflow_user['name']}] agents were deleted successfully.")
        else:
            raise ValueError('You must provide a workflow.')

    def clean_environment(self):
        self.delete_workflows()
        self.stop_agents()
        # delete role
        self.kubeclient.delete_rolebinding(self.namespace)
        logging.info(f'[++]Delete rolebinding default-admin')
        # delete namespace
        self.kubeclient.delete_namespace(self.namespace)
        logging.info(f'[++]Delete namespace "{self.namespace}"')
