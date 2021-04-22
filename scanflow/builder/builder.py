from scanflow.app import Application, Executor, Workflow
from scanflow.tracker import Tracker
from scanflow.agent import Agent

from typing import List, Dict

class Builder():
    def __init__(self,
                 app: Application,
                 registry: str = None):
        self.registry = registry
        self.app = app

    def build_ScanflowApplication(self):
        # build scanflow tracker
        self.build_ScanflowTracker(self.app.local_tracker)
        # build scanflow agent
        self.build_ScanflowAgents(self.app.agents)
        # build scanflow workflows - executors
        self.build_ScanflowWorkflows(self.app.workflows)


    def build_ScanflowTracker(self, tracker: Tracker):
        print("")


    def build_ScanflowAgents(self, agents: List[Agent]):
        print("")
    
    
    def build_ScanflowWorkflows(self, workflows: List[Workflow]): 
        print("")

    def build_ScanflowExecutors(self, executors: List[Executor]):
        print("")