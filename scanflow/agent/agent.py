from scanflow.tools.scanflowtools import get_scanflow_paths, check_verbosity

class Agent():
    def __init__(self,
                 name: str,
                 template: str = None,
                 mainfile: str = None,
                 parameters: dict = None,
                 dockerfile: str = None,
                 image: str = None,
                 verbose: bool = False):
        
        self.name = name
        self.template = template
        self.mainfile = mainfile
        self.parameters = parameters
        self.dockerfile = dockerfile
        self.image = image
        self.verbose = verbose
        check_verbosity(verbose)

#    @property
#    def image(self):
#        return self.__image
#
#    @image.setter
#    def image(self,
#              image: str):
#        self.__image = image
#
    def to_dict(self):
        tmp_dict = {}
        agent_dict = self.__dict__
        for k, v in agent_dict.items():
            tmp_dict[k] = v
        return tmp_dict
        
