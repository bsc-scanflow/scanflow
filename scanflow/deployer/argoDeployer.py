import logging
import os

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