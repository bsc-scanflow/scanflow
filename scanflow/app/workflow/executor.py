

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
                 base_image: str = None,
                 env: dict = None,
                 image: str = None):

        super(Executor, self).__init__(name=name)
        self.mainfile = mainfile
        self.parameters = parameters
        self.requirements = requirements
        self.dockerfile = dockerfile
        self.base_image = base_image
        self.env = env
        self.image = image

#    @property
#    def image(self):
#        return self.__image
#
#    @image.setter
#    def image(self,
#              image: str):
#        self.__image = image