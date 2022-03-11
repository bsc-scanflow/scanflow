import logging
import subprocess
import os
from typing import List
import docker
import requests
import datetime

from scanflow.app import Workflow

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool

import scanflow.deployer.deployer as deployer
from scanflow.templates import Kubernetes

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

from scanflow.deployer.utils import (
    get_output_dir,
    set_output_dir,
    is_output_dir_set,
)

class VolcanoDeployer(deployer.Deployer):
    def __init__(self,
                 k8s_config_file=None):
        super(VolcanoDeployer, self).__init__(k8s_config_file)
        
        self.volcanoJobs = None

    def run_workflow(self, 
                     namespace: str, 
                     workflow: Workflow):
        """
        run workflow by volcano
        """
        if workflow.type == 'mpi':
            workflow_name = workflow.name
            #mpi workflow now only support one node to be deployed as a volcanojob
            vj_body = workflow.nodes[0].body
        
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
                
            #1. volume mount
            volumestr = [{'mountPath': output_dir, 'volumeClaimName': workflow_name}]
            vj_body['spec']['volumes'] = volumestr
            
            #2. name
            vj_body['metadata']['name'] = workflow_name
            
            vj = self.kubeclient.create_volcanoJob(namespace, vj_body)
            logging.info(f"[+++] Workflow: [{workflow_name}] has been submitted to volcano {vj}")

            if vj is not None:
                return True
            else:
                return False
        else:
            logging.error(f"[**] Workflow [{workflow}] is not mpi")
           
    
    def delete_workflows(self,
                         namespace: str,
                         workflows: List[Workflow]):
        deleted = True
        for workflow in workflows:
            deleted = deleted and self.kubeclient.delete_workflow(namespace, workflow)       
        return deleted
    
    def delete_workflow(self, namespace: str, workflow: Workflow):
        deleted = False
        try:
            result = self.kubeclient.delete_volcanoJob(namespace, workflow.name)
            if result is not None:
                deleted = True
        except:
            logging.info(f"can not find vj {workflow.name}")
        finally:
            #outputdir
            self.kubeclient.delete_persistentvolumeclaim(namespace, workflow.name)
            self.kubeclient.delete_persistentvolume(workflow.name)
            return deleted