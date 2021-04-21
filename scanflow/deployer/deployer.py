"""
abstract deployer class
"""
import logging

from scanflow.tools.scanflowtools import get_scanflow_paths, check_verbosity
from scanflow.templates import Kubernetes


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class Deployer():
    def __init__(self,
                 verbose=True):
        self.verbose = verbose
        check_verbosity(verbose)

    def create_environment(self, app_name, team_name):
        """
          create namespace, secret...
        """
        self.namespace = f"{app_name}-{team_name}"
        logging.info(f'[++]Creating namespace "{self.namespace}"')

        

    def start_local_tracker(self):
        """
          deploy tracker in namespaced env
        """
        raise NotImplementedError("")

    def stop_local_tracker(self):
        """
          stop local_tracker
        """
        raise NotImplementedError("")

    def start_agents(self):
        """
          deploy agents
        """
        raise NotImplementedError("Backend:start_agents")

    def stop_agents(self):
        """
           stop agents
        """
        raise NotImplementedError("Backend:stop_agents")

    def run_workflows(self):
        """
           run batch workflow
        """
        raise NotImplementedError("Backend:run_workflows")

    def delete_workflows(self):
        """
           delete batch workflow
        """
        raise NotImplementedError("Backend:delete_workflows")

    def clean_environment(self):
        """
           delete workflow and stop agents
        """
        raise NotImplementedError("Backend:clean env")

    
