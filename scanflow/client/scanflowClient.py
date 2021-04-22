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

#scanflow builder
from scanflow.builder import Builder

from scanflow.tools.scanflowtools import check_verbosity
from scanflow.server.utils import (
    set_server_uri,
    is_server_uri_set,
    get_server_uri,
)


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ScanflowClient:
    def __init__(self,
                 scanflow_server_uri=None,
                 verbose=True):
        """
        """
        self.verbose = verbose
        check_verbosity(verbose)
        
        if scanflow_server_uri is not None:
            set_server_uri(scanflow_server_uri)
        if not is_server_uri_set():
            raise ValueError("Scanflow_server_uri is not provided")
        self.scanflow_server_uri = get_server_uri()

## scanflow app build
    def build_ScanflowApplication(self,
                                  app: Application,
                                  registry: str = None):
        builder = Builder(app,registry) 
        builder.build_ScanflowApplication()


###   Scanflow graph

#    def draw_ScanflowApplication(self, scanflowapp, verbose=False):
#        appGraph = ApplicationGraph(scanflowapp, verbose=verbose)
#        return appGraph.draw_graph()
#


###   Scanflow app
    def ScanflowExecutor(self,
                         name: str,
                         mainfile: str,
                         parameters: dict = None,
                         requirements: str = None,
                         dockerfile: str = None,
                         env: str = None):
        return Executor(name, mainfile, parameters, requirements, dockerfile, env)

    def ScanflowDependency(self,
                         dependee: str,
                         depender: str,
                         priority: int = 0):
        return Dependency(dependee, depender, priority)

    def ScanflowWorkflow(self,
                         name: str,
                         executors: List[Executor],
                         dependencies: List[Dependency]):
        return Workflow(name, executors, dependencies)

    def ScanflowAgent(self,
                      agent_name: str,
                      agent_dir: str,
                      agent_type: str,
                      verbose: bool = False):
        return Agent(agent_name, agent_type, agent_dir, verbose)
    
    def ScanflowApplication(self,
                            app_name: str,
                            app_dir: str,
                            team_name: str,
                            workflows: List[Workflow]=None,
                            agents: List[Agent]=None,
                            verbose: bool = False):
        return Application(app_name, app_dir, team_name, workflows, agents, verbose)

