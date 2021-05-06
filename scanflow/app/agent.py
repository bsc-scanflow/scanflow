class Agent():
    def __init__(self,
                 name: str,
                 template: str = None,
                 mainfile: str = None,
                 parameters: dict = None,
                 dockerfile: str = None,
                 image: str = None):
        """
           we provide several templates. the functions within the templates need to be used together with the agent file.
           user can also define their own agent and provide the mainfile.
        """
        
        self.name = name
        self.template = template
        self.mainfile = mainfile
        self.parameters = parameters
        self.dockerfile = dockerfile
        self.image = image

    def to_dict(self):
        tmp_dict = {}
        agent_dict = self.__dict__
        for k, v in agent_dict.items():
            tmp_dict[k] = v
        return tmp_dict
        
