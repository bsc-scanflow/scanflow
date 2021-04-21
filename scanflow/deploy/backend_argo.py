import logging
import subprocess
import os
import docker
import requests
import datetime

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool

import scanflow.deploy.backend as backend
from scanflow.templates import Kubernetes, ArgoWorkflows

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)



class BackendArgo(backend.Backend):
    def __init__(self,
                 # app_dir=None,
                 workflower=None,
                 namespace=None,
                 registry=None,
                 k8sconfigdir=None,
                 verbose=True):
        super(BackendArgo, self).__init__(workflower,verbose)

        if k8sconfigdir is not None:
            self.kubeclient = Kubernetes(configdir=k8sconfigdir, verbose=self.verbose)
            self.argoclient = ArgoWorkflows(configdir=k8sconfigdir, verbose=self.verbose)
        else:
            self.kubeclient = Kubernetes()
            self.argoclient = ArgoWorkflows()
 
        if namespace is not None:
            self.namespace = namespace
            logging.info(f'[++]Creating namespace "{namespace}"')
            self.kubeclient.create_namespace(namespace)
        else:
            self.namespace = 'default'
            logging.info(f'[++]Using default namespace "{namespace}"')
        
        logging.info(f"[++]Creating Role for 'default service account'")
        rolebinding = self.kubeclient.build_rolebinding(self.namespace)
        self.kubeclient.create_rolebinding(self.namespace, rolebinding)

        self.registry = registry        

    def pipeline(self):
        self.build_workflows()
        self.start_workflows()
        self.run_workflows()


    def build_workflows(self):

        self.workflows = list()

        os.makedirs(self.paths['meta_dir'], exist_ok=True)
        os.makedirs(self.paths['ad_tracker_dir'], exist_ok=True)
        os.makedirs(self.paths['ad_checker_dir'], exist_ok=True)
        os.makedirs(self.paths['improver_dir'], exist_ok=True)
        os.makedirs(self.paths['planner_dir'], exist_ok=True)
        os.makedirs(self.paths['deployer_dir'], exist_ok=True)


        for wf_user in self.workflows_user:
            logging.info(f"[++] Building workflow: [{wf_user['name']}].")
            environments = self.__build_workflow(wf_user)
            logging.info(f"[+] Workflow: [{wf_user['name']}] was built successfully.")
            workflow = {'name': wf_user['name'],
                        'nodes': environments}

            self.workflows.append(workflow)

        tools.save_workflows(self.paths, self.workflows)

    def __build_workflow(self, workflow: dict):
        """
        Build Docker images
        Build agents deployment file
        Build Workflow deployment file
        """

        environments = []
        for wflow in workflow['executors']:

            logging.info(f"[+] Building env: [{workflow['name']}:{wflow['name']}].")

            env_image_name = f"{wflow['name']}"

            # Save each python file to compose-verbose folder
            meta_compose_dir = os.path.join(self.paths['ad_meta_dir'], 'compose-verbose')
            source = os.path.join(self.app_dir, 'workflow', wflow['file'])
            copy2(source, meta_compose_dir)

            # Create Dockerfile if needed and build dockerimages to registry
            if 'requirements' in wflow.keys():
                meta_compose_dir = os.path.join(self.paths['ad_meta_dir'], 'compose-verbose')

                dockerfile_path = tools.generate_dockerfile(folder=meta_compose_dir,
                                                            executor=wflow,
                                                            dock_type='executor',
                                                            port=None)
                source = os.path.join(self.app_dir, 'workflow', wflow['requirements'])
                copy2(source, meta_compose_dir)
                metadata = tools.build_image_to_registry(self.registry, env_image_name, meta_compose_dir, dockerfile_path)
                environments.append(metadata)

            elif 'dockerfile' in wflow.keys():
                meta_compose_dir = os.path.join(self.paths['ad_meta_dir'], 'compose-verbose')

                dockerfile_dir = os.path.join(self.app_dir, 'workflow') #context
                dockerfile_path = os.path.join(dockerfile_dir, wflow['dockerfile'])
                copy2(dockerfile_path, meta_compose_dir)
                metadata = tools.build_image_to_registry(self.registry, env_image_name, dockerfile_dir, dockerfile_path)
                environments.append(metadata)



        if 'tracker' in workflow.keys():
            port = workflow['tracker']['port']
            meta_compose_dir = os.path.join(self.paths['ad_meta_dir'], 'compose-verbose')
            dockerfile_path = tools.generate_dockerfile(folder=meta_compose_dir,
                                                        executor=workflow,
                                                        dock_type='tracker',
                                                        port=port)


            tracker_image_name = f"tracker-{workflow['name']}"
            tracker_dir = os.path.join(self.paths['ad_tracker_dir'], tracker_image_name )
            metadata = tools.build_image_to_registry(self.registry, tracker_image_name, meta_compose_dir,
                                         dockerfile_path, 'tracker', port, tracker_dir)
            environments.append(metadata)

            if workflow['tracker']['mode'] == 'online':
                port_agent = port + 1
                dockerfile_agent_path = tools.generate_dockerfile(folder=meta_compose_dir,
                                                                  executor=workflow,
                                                                  dock_type='tracker_agent',
                                                                  port=port_agent)

                tracker_agent_image_name = f"tracker-agent-{workflow['name']}"
                tracker_dir = os.path.join(self.paths['ad_tracker_dir'], tracker_image_name )
                metadata = tools.build_image_to_registry(self.registry, tracker_agent_image_name, meta_compose_dir,
                                             dockerfile_agent_path, 'tracker-agent', port_agent, tracker_dir)

                environments.append(metadata)
                

            if 'checker' in workflow.keys():
                port = workflow['checker']['port']
                meta_compose_dir = os.path.join(self.paths['ad_meta_dir'], 'compose-verbose')
                dockerfile_path = tools.generate_dockerfile(folder=meta_compose_dir,
                                                            executor=workflow,
                                                            dock_type='checker',
                                                            port=port)


                checker_image_name = f"checker-{workflow['name']}"
                checker_dir = os.path.join(self.paths['ad_checker_dir'], checker_image_name )
                metadata = tools.build_image_to_registry(self.registry, checker_image_name, meta_compose_dir,
                                             dockerfile_path, 'checker', port, checker_dir)
                environments.append(metadata)



                if workflow['checker']['mode'] == 'online':
                    port_agent = port + 1
                    dockerfile_agent_path = tools.generate_dockerfile(folder=meta_compose_dir,
                                                                      executor=workflow,
                                                                      dock_type='checker_agent',
                                                                      port=port_agent)

                    checker_agent_image_name = f"checker-agent-{workflow['name']}"
                    checker_dir = os.path.join(self.paths['ad_checker_dir'], checker_agent_image_name )
                    metadata = tools.build_image_to_registry(self.registry, checker_agent_image_name, meta_compose_dir, dockerfile_agent_path, 'checker-agent', port_agent, checker_dir)

                    environments.append(metadata)
                    

            if 'improver' in workflow.keys():
                meta_compose_dir = os.path.join(self.paths['ad_meta_dir'], 'compose-verbose')

                if workflow['improver']['mode'] == 'online':
                    port_agent = workflow['improver']['port']
                    dockerfile_agent_path = tools.generate_dockerfile(folder=meta_compose_dir,
                                                                      executor=workflow,
                                                                      dock_type='improver_agent',
                                                                      port=port_agent)

                    improver_agent_image_name = f"improver-agent-{workflow['name']}"
                    improver_dir = os.path.join(self.paths['improver_dir'], improver_agent_image_name )
                    metadata = tools.build_image_to_registry(self.registry, improver_agent_image_name, meta_compose_dir,
                                                 dockerfile_agent_path, 'improver-agent', port_agent, improver_dir)

                    environments.append(metadata)
                     
                    
                else:
                    raise ValueError('Improver can be only deployed in online mode. Please set mode=online.')

            if 'planner' in workflow.keys():
                meta_compose_dir = os.path.join(self.paths['ad_meta_dir'], 'compose-verbose')

                if workflow['planner']['mode'] == 'online':
                    port_agent = workflow['planner']['port']
                    dockerfile_agent_path = tools.generate_dockerfile(folder=meta_compose_dir,
                                                                      executor=workflow,
                                                                      dock_type='planner_agent',
                                                                      port=port_agent)

                    planner_agent_image_name = f"planner-agent-{workflow['name']}"
                    planner_dir = os.path.join(self.paths['planner_dir'], planner_agent_image_name )
                    metadata = tools.build_image_to_registry(self.registry, planner_agent_image_name, meta_compose_dir,
                                                 dockerfile_agent_path, 'planner-agent', port_agent, planner_dir)

                    environments.append(metadata)
                else:
                    raise ValueError('Planner can be only deployed in online mode. Please set mode=online.')

            return environments

        return environments


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
