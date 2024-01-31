import logging
import os

from typing import List
from scanflow.app import Workflow, Executor

import scanflow.deployer.deployer as deployer
from scanflow.templates import ArgoWorkflows
from scanflow.deployer.env import ScanflowSecret, ScanflowClientConfig
from scanflow.tools.param import format_parameters, format_command

from kubernetes.client import V1ResourceRequirements

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
            if workflow.type == 'batch':
                logging.info(f"[++] Running workflow: [{workflow.name}].")
                submitted = submitted and self.run_workflow(namespace, workflow)
                logging.info(f"[+] Workflow: [{workflow.name}] was run successfully.")
            else:
                logging.error(f"[**] Workflow [{workflow.name}] is not batch")
        return submitted

    def run_workflow(self, 
                     namespace : str,
                     workflow: Workflow):
        """
        run workflow by argo
        """
        if workflow.type == 'batch':
            workflow_name = workflow.name
            if workflow.affinity:
                if isinstance(workflow.affinity, dict):
                    workflow_affinity = workflow.affinity
                else:
                    workflow_affinity = workflow.affinity.to_dict()
            else:
                workflow_affinity = None
                
            self.argoclient.configWorkflow(workflow_name, workflow_affinity)

            #output volume - deleted mode
            if workflow.output_dir is not None:
                set_output_dir(workflow.output_dir)
            output_dir = get_output_dir()
            logging.info(f"[+] output dir {output_dir}")
            # logging.info(f"[+] Create {workflow_name} output PV")
            # pv = self.kubeclient.build_persistentvolume(workflow_name, "1Gi", f"/gpfs/bsc_home/xpliu/pv/scanflow-output/{workflow_name}-output")
            # step1 = self.kubeclient.create_persistentvolume(body=pv)
            step1 = True
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
            for executor in workflow.nodes:
                #volumeMounts = self.argoclient.buildVolumeMounts(outputpath=output_dir)
                volumeMounts = self.argoclient.buildVolumeMounts(outputpath=output_dir, scanflowpath="/scanflow")
                logging.info(f"[+] Building workflow: [{workflow.name}:{executor.name}].")
                if executor.env is not None:
                    env.update(executor.env)
               
                if executor.resources is not None:            
                    logging.info(f"{executor.resources}")
                    logging.info(f"{executor.resources.to_dict().get('limits')}")
                    argoContainers[f"{executor.name}"] = self.argoclient.argoExecutor(name = executor.name, 
                             image = executor.image,
                             image_pull_policy = None,
                             command = format_command({'python': f'/app/{executor.name}/{executor.mainfile}'})+format_parameters(executor.parameters),
                             args = [],
                            #  args = format_parameters(executor.parameters),
                             env = env, 
                             volumeMounts = volumeMounts,
                             resources = executor.resources.to_dict().get('limits'))
                else:
                    logging.info(f" parameters: {format_parameters(executor.parameters)}")
                    logging.info(f" command: {format_command({'python': f'/app/{executor.name}/{executor.mainfile}'})}")
                    argoContainers[f"{executor.name}"] = self.argoclient.argoExecutor(name = executor.name, 
                             image = executor.image,
                             image_pull_policy = None,
                             command = format_command({'python': f'/app/{executor.name}/{executor.mainfile}'})+format_parameters(executor.parameters),
                            #  args = format_parameters(executor.parameters),
                             args = [],
                             env = env, 
                             volumeMounts = volumeMounts,
                             resources=None)

            #edges
            logging.info(f"[+] Building workflow: [{workflow_name}- edges]")
            edge_graph = []
            if workflow.edges:
                for edge in workflow.edges:
                    edge_graph.append(
                        [argoContainers[f"{edge.dependee}"],
                         argoContainers[f"{edge.depender}"]]
                    )
            else:
                edge_graph.append([argoContainers[workflow.nodes[0].name]])

            #dag
            logging.info(f"[+] Building workflow: [{workflow_name}- dag]")
            self.argoclient.argoDag(edge_graph)

            argoWorkflow = self.argoclient.submitWorkflow(namespace)
            logging.info(f"[+++] Workflow: [{workflow_name}] has been submitted to argo {argoWorkflow}")

            if argoWorkflow is not None:
                return True
            else:
                return False
        else:
            logging.error(f"[**] Workflow [{workflow}] is not batch")

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