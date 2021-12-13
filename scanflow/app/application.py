from typing import List, Dict
import logging

from scanflow.app.agent.agent import Agent
from scanflow.app.workflow.workflow import Workflow
from scanflow.app import Tracker

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class Application:
    """
      set an application
    """
    def __init__(self,
                 app_name: str,
                 app_dir: str,
                 team_name: str,
                 workflows: List[Workflow] = None,
                 agents: List[Agent] = None,
                 tracker: Tracker = None):

        self.app_name = app_name
        self.app_dir = app_dir
        self.team_name = team_name
        self.workflows = workflows
        self.agents = agents
        self.tracker = tracker

    def to_dict(self):
        tmp_dict = {}
        app_dict = self.__dict__
        for k, v in app_dict.items():
            if k == 'workflows' and v is not None:
                workflows_list = list()
                for workflow in v:
                    workflows_list.append(workflow.to_dict())
                tmp_dict[k] = workflows_list  
            elif k == 'agents' and v is not None:
                agents_list = list()
                for agent in v:
                    agents_list.append(agent.to_dict())
                tmp_dict[k] = agents_list
            elif k == 'tracker' and v is not None:
                tmp_dict[k] = v.__dict__
            else:
                tmp_dict[k] = v
            
        # logging.info(f"Scanflowapp: {tmp_dict}")
        return tmp_dict



