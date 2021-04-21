from scanflow.tools.scanflowtools import get_scanflow_paths, check_verbosity

class Agent():
    def __init__(self,
                 agent_name: str,
                 agent_type: str,
                 agent_dir: str,
                 verbose: bool = False):
        
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.agent_dir = agent_dir
        self.verbose = verbose
        check_verbosity(verbose)

    def to_dict(self):
        tmp_dict = {}
        agent_dict = self.__dict__
        for k, v in agent_dict.items():
            tmp_dict[k] = v
        return tmp_dict
        
