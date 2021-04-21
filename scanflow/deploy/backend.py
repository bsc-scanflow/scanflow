"""
abstract backend class
"""
from scanflow.tools.scanflowtools import get_scanflow_paths, check_verbosity

class Backend():
    def __init__(self,
                 workflower=None,
                 verbose=True):
        self.verbose = verbose
        if workflower is not None:
            self.app_name = workflower.app_name
            self.app_dir = workflower.app_dir
            self.paths = get_scanflow_paths(workflower.app_dir)
            self.workflows_user = workflower.workflows_user
        else:
            self.workflows_user = None
        check_verbosity(verbose)

    
    def build_workflows(self):
        """
         genterate agent/workflow dockerfile
        """
        raise NotImplementedError("Backend:build_workflows")

    def start_workflows(self):
        raise NotImplementedError("Backend:start_workflows")

    def stop_workflows(self):
        raise NotImplementedError("Backend:stop_workflows")

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

    
