

class Node():
    """
        Abstract base Node class.

    """
    def __init__(self, name: str):
        self.name = name

class Executor(Node):
    """
        Minimal unit of execution.

    """
    def __init__(self,
                 name: str,
                 mainfile: str,
                 parameters: dict = None,
                 requirements: str = None,
                 dockerfile: str = None,
                 env: dict = None):

        super(Executor, self).__init__(name=name)
        self.mainfile = mainfile
        self.parameters = parameters
        self.requirements = requirements
        self.dockerfile = dockerfile
        self.env = env

    @property
    def image(self):
        return self.image

    @image.setter
    def image(self,
              image: str):
        self.image = image