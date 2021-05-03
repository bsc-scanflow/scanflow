import logging
import os

from typing import List, Dict

# scanflow app
from scanflow.app import Executor, Dependency, Workflow, Application, Tracker
from scanflow.agent import Agent

# scanflow graph
#from scanflow.graph import ApplicationGraph


from scanflow.tools.scanflowtools import check_verbosity
from scanflow.server.utils import (
    set_server_uri,
    is_server_uri_set,
    get_server_uri,
)
import requests
import json


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ScanflowClient:
    def __init__(self,
                 builder: str = "docker",
                 registry : str = "172.30.0.49:5000",
                 scanflow_server_uri : str = None,
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

        self.builderbackend = self.get_builder(builder, registry)

    def get_builder(self, builder, registry):
        if builder == "docker":
            from scanflow.builder import DockerBuilder
            return DockerBuilder(registry)
        else:
            logging.info(f"unknown builder backend {builder}")

    def build_ScanflowApplication(self,
                                  app: Application, trackerPort: int):
        #build scanflowapp
        return self.builderbackend.build_ScanflowApplication(app, trackerPort)

    def submit_ScanflowApplication(self,
                                   app: Application):
        url = f"{self.scanflow_server_uri}/submit/scanflowApplication" 
        response = requests.post(url=url, 
        data= json.dumps(app.to_dict()),
        headers={"accept": "application/json"})

        if json.loads(response.text)['status'] == 0:
            return True
        else:
            logging.error(f"submit scanflow application error {response.text['status']}")
            return False


###   Scanflow graph

#    def draw_ScanflowApplication(self, scanflowapp):
#        appGraph = ApplicationGraph(scanflowapp)
#        return appGraph.draw_graph()



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
                         dependencies: List[Dependency],
                         output_dir: str = None):
        return Workflow(name, executors, dependencies, output_dir)

    def ScanflowAgent(self,
                      name: str,
                      template: str,
                      mainfile: str = None,
                      parameters: dict = None):
        return Agent(name, template, mainfile, parameters)
    
    def ScanflowApplication(self,
                            app_name: str,
                            app_dir: str,
                            team_name: str,
                            workflows: List[Workflow]=None,
                            agents: List[Agent]=None,
                            tracker: Tracker = None):
        return Application(app_name, app_dir, team_name, workflows, agents, tracker)

