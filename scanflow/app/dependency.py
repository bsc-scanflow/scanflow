class Edge():
    """
       Abstract class of relation
    """
    def __init__(self, 
                 dependee: str,
                 depender: str):
        self.depender = depender
        self.dependee = dependee


class Dependency(Edge):
    """
      Scanflow relation
    """
    def __init__(self,
                 dependee: str = None,
                 depender: str = None,
                 priority: int = 0):
        """
          a relation from dependee to depender, will generate a edge from dependee -> depender
        """
        super(Dependency, self).__init__(dependee=dependee,
                                       depender=depender)
        self.priority = priority
                    