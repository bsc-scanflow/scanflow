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
                 k8s_config_file=None,
                 verbose=True):
        self.verbose = verbose
        check_verbosity(verbose)

        self.kubeclient = Kubernetes(k8s_config_file=k8s_config_file, 
        verbose = verbose)


    def create_environment(self, app):
        """
          create namespace, role, agents...
        """
        # 1. create namespace
        step1 = self.create_namespace(app)
        # 2. create role
        step2 = self.create_role()
        # 3. start_local_tracker
        step3 = self.start_local_tracker()
        # 4. start_agent if has
        step4 = self.start_agents()

        return  step1 and step2 and step3 and step4 

    def clean_environment(self):
        """
           delete env and stop agents
        """
        # 1. delete agent
        step1 = self.stop_agents()
        # 2. delete local_tracker
        step2 = self.stop_local_tracker()
        # 3. delete role
        step3 = self.delete_role() 
        # 4. delete namespace
        step4 = self.delete_namespace()
        
        return step1 and step2 and step3 and step4

    def create_namespace(self, app):
        self.namespace = f"{app.app_name}-{app.team_name}"
        logging.info(f'[++]Creating namespace "{self.namespace}"')
        return self.kubeclient.create_namespace(self.namespace)

    def delete_namespace(self):
        logging.info(f'[++]Delete namespace "{self.namespace}"')
        return self.kubeclient.delete_namespace(self.namespace)

    def create_role(self):
        logging.info(f"[++]Creating Role for 'default service account'")
        rolebinding = self.kubeclient.build_rolebinding(self.namespace)
        return self.kubeclient.create_rolebinding(self.namespace, rolebinding)

    def delete_role(self):
        logging.info(f'[++]Delete rolebinding default-admin')
        return self.kubeclient.delete_rolebinding(self.namespace)

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

    
