import logging
import os

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool
from typing import List, Dict

# scanflow app
from scanflow.app import Executor, Dependency, Workflow, Application
from scanflow.agent import Agent

# scanflow graph
#from scanflow.graph import ApplicationGraph

# scanflow deployer


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ScanflowClient:
    def __init__(self,
                 scanflow_controller_uri=None,
                 registry=None,
                 deployer="argo",
                 scanflowType="local",
                 verbose=True):
        """
            scanflowClient = ScanflowClient()
            scanflow_controller_uri=http://172.30.0.50:46666
                      =http://scanflow-controller-service.scanflow-system.svc.cluster.local
            general backend for scanflow is kubernetes
            deployer: deploy backend to run workflows
                      for offline batch usually use 'argo'
                      for online inference usually use 'seldon'
            type: scanflow type, if 'local' means you could call deployer from local. if 'server' means you will call scanflow server to use deployer
        """
        self.verbose = verbose
        check_verbosity(verbose)
        self.scanflow_controller_uri = scanflow_controller_uri
        self.registry = registry
        self.scanflowType = scanflowType
        self.deployer = get_deployer(deployer)

### Scanflow deploy
    def get_deployer(self, deployer):
        if self.scanflowType == "local":
            if deployer == "argo":
                from scanflow.deployer.argoDeployer import ArgoDeployer
                return ArgoDeployer(self.verbose)
            elif deployer == "volcano":
                from scanflow.deployer.volcanoDeployer import VolcanoDeployer
                return VolcanoDeployer(self.verbose)
            elif deployer == "seldon":
                from scanflow.deployer.seldonDeployer import seldonDeployer
                return SeldonDeployer(self.verbose)
            else:
                raise ValueError("unknown deployer: " + deployer)
        elif self.scanflowType == "server":
            return None
        else:
            logging.info("Cannot find scanflowType")

    def create_environment(self, app_name, team_name):
        if self.scanflowType == "local":
            if deployer == "argo":
                from scanflow.deployer.argoDeployer import ArgoDeployer
                self.deployer = ArgoDeployer(self.verbose)
            elif deployer == "volcano":
                logging.info("volcano backend is not ready!")
            elif deployer == "seldon":
                logging.info("seldon backend is not ready!")
            else:
                raise ValueError("unknown deployer: " + deployer)
        elif self.scanflowType == "server":
            
        else:
            logging.info("Cannot find scanflowType")




###   Scanflow graph

#    def draw_ScanflowApplicationGraphs(self, scanflowapp, verbose=False):
#        appGraph = ApplicationGraph(scanflowapp, verbose=verbose)
#        return appGraph.draw_graph()
#


###   Scanflow app
    def ScanflowExecutor(self,
                         name: str = None,
                         mainfile: str = None,
                         parameters: dict = None,
                         requirements: str = None,
                         dockerfile: str = None,
                         env: str = None):
        return Executor(name, mainfile, parameters, requirements, dockerfile, env)

    def ScanflowDependency(self,
                         dependee: str = None,
                         depender: str = None,
                         priority: int = 0):
        return Dependency(dependee, depender, priority)

    def ScanflowWorkflow(self,
                         name: str = None,
                         executors: List[Executor] = None,
                         dependencies: List[Dependency] = None):
        return Workflow(name, executors, dependencies)

    def ScanflowAgent(self,
                      agent_name: str,
                      agent_type: str,
                      agent_dir: str,
                      verbose: bool = False):
        return Agent(agent_name, agent_type, agent_dir, verbose)
    
    def ScanflowApplication(self,
                            app_name: str,
                            app_dir: str,
                            team_name: str,
                            workflows: List[Workflow] = None,
                            agents: List[Agent]=None,
                            verbose: bool = False):
        return Application(app_name, app_dir, team_name, workflows, agents, verbose)
    