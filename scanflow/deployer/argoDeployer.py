import logging
import os

from typing import List
from scanflow.app import Workflow, Executor

import scanflow.deployer.deployer as deployer
from scanflow.templates import ArgoWorkflows
from scanflow.deployer.env import ScanflowSecret, ScanflowClientConfig
from scanflow.tools.param import format_parameters

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

        self.argoclient = ArgoWorkflows(k8s_config_file=k8s_config_file)

    def run_workflows(self, 
                      namespace : str,
                      workflows : List[Workflow]):
        submitted = True
        for workflow in workflows:
            logging.info(f"[++] Running workflow: [{workflow.name}].")
            submitted = submitted and self.run_workflow(namespace, workflow)
            logging.info(f"[+] Workflow: [{workflow.name}] was run successfully.")
        return submitted

    def run_workflow(self, 
                     namespace : str,
                     workflow: Workflow):
        """
        run workflow by argo
        """
        workflow_name = workflow.name
        self.argoclient.configWorkflow(workflow_name)

        #output volume - deleted mode
        if workflow.output_dir is not None:
            set_output_dir(workflow.output_dir)
        output_dir = get_output_dir()
        logging.info(f"[+] output dir {output_dir}")
        logging.info(f"[+] Create {workflow_name} output PV")
        pv = self.kubeclient.build_persistentvolume(workflow_name, "1Gi", f"/gpfs/bsc_home/xpliu/pv/scanflow-output/{workflow_name}-output")
        step1 = self.kubeclient.create_persistentvolume(body=pv)
        logging.info(f"[+] Create {workflow_name} output PVC")
        pvc = self.kubeclient.build_persistentvolumeclaim(namespace, workflow_name, None,"ReadWriteMany", "512Mi")
        step2 = self.kubeclient.create_persistentvolumeclaim(namespace, pvc)
        if step1 and step2:
            logging.info("output dir created")

        #volume
        #self.argoclient.buildVolumes(outputpath=workflow_name)
        self.argoclient.buildVolumes(outputpath=workflow_name, scanflowpath=f"scanflow-{namespace}")
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
            #volumeMounts = self.argoclient.buildVolumeMounts(outputpath=output_dir)
            volumeMounts = self.argoclient.buildVolumeMounts(outputpath=output_dir, scanflowpath="/scanflow")
            logging.info(f"[+] Building workflow: [{workflow.name}:{executor.name}].")
            logging.info(f"{format_parameters(executor.parameters)}")
            argoContainers[f"{executor.name}"] = self.argoclient.argoExecutor(name = executor.name, 
                         image = executor.image,
                         args = format_parameters(executor.parameters),
                         env = env, 
                         volumeMounts = volumeMounts)

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

        if argoWorkflow is not None:
            return True
        else:
            return False

    def delete_workflows(self,
                         namespace: str,
                         workflows: List[Workflow]):
        """
        delete argo workflows
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
            result = self.argoclient.deleteWorkflow(namespace, workflow_name)
            if result is not None:
                deleted = True
        except:
            logging.info(f"cannot find workflows")
        finally:
            #output dir
            self.kubeclient.delete_persistentvolumeclaim(namespace, workflow_name)
            self.kubeclient.delete_persistentvolume(workflow_name)
            return deleted

    def run_executor(self,
                 namespace: str,
                 executor: Executor):
        pass

    def delete_executor(self,
                        namespace: str,
                        executor: Executor):
        pass