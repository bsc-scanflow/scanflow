import logging
import os

import scanflow.deployer.deployer as deployer
from scanflow.templates import ArgoWorkflows
from scanflow.deployer.env import ScanflowSecret, ScanflowClientConfig

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

from scanflow.deployer.utils import (
    get_output_dir,
    set_output_dir,
    is_output_dir_set,
)

class ArgoDeployer(deployer.Deployer):
    def __init__(self,
                 k8s_config_file=None):
        super(ArgoDeployer, self).__init__(k8s_config_file)

        self.argoclient = ArgoWorkflows()

    def run_workflows(self, 
                      namespace : str,
                      workflows : List[Workflow]):

        for workflow in workflows:
            logging.info(f"[++] Running workflow: [{workflow.name}].")
            self.run_workflow(namespace, workflow)
            logging.info(f"[+] Workflow: [{workflow.name}] was run successfully.")

    def run_workflow(self, 
                     namespace : str,
                     workflow: Workflow):
        """
        run workflow by argo
        """
        workflow_name = workflow.name

        #output volume - deleted mode
        if workflow.output_dir is not None:
            set_output_dir(workflow.output_dir)
        output_dir = get_output_dir()
        logging.info(f"[+] Create {workflow_name} output PVC")
        pvc = self.kubeclient.build_persistentvolumeclaim(namespace, workflow_name, "local-path", "ReadWriteOnce", "512Mi")
        result = self.kubeclient.create_persistentvolumeclaim(namespace, pvc)
        if result:
            #volume
            self.argoclient.buildVolumes(outputpath=workflow_name)
            #env
            ss = ScanflowSecret()
            scc = ScanflowClientConfig()
            scc.SCANFLOW_TRACKER_LOCAL_URI = f"http://scanflow-tracker.{namespace}.svc.cluster.local"
            env = ss.__dict__
            env.update(scc.__dict__)
            logging.info(f"env for executor {env}")

            #executor
            argoContainers = {}
            for executor in workflow.executors:
                volumeMounts = self.argoclient.buildVolumeMounts(outputpath=f"{output_dir}/{executor.name}")
                logging.info(f"[+] Building workflow: [{workflow.name}:{executor.name}].")
                argoContainers[f"{executor.name}"] = self.argoclient.argoExecutor(executor.name, executor.image, env, volumeMounts)

            #dependencies
            logging.info(f"[+] Building workflow: [{workflow_name}- dependencies]")
            dependency_graph = []
            for dependency in workflow.dependencies:
                dependency_graph.append(
                    [argoContainers[f"{dependency.dependee}"],
                     argoContainers[f"{dependency.depender}"]]
                )

            #dag
            logging.info(f"[+] Building workflow: [{workflow_name}- dag]")
            self.argoclient.argoDag(dependency_graph)

            argoWorkflow = self.argoclient.submitWorkflow(namespace)
            logging.info(f"[+++] Workflow: [{workflow_name}] has been submitted to argo {argoWorkflow}")

    def run_executor(self,
                     namespace: str,
                     executor: Executor):
        pass


    def delete_workflows(self,
                         namespace: str,
                         workflows: List[Workflow]):
        """
        delete argo workflows
        """
        for workflow in workflows:
            self.delete_workflow(namespace, workflow)

    def delete_workflow(self, 
                        namespace: str,
                        workflow: Workflow):
        pass