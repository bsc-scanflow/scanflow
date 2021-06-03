class Edge():
    """
       Abstract class of relation
    """
    def __init__(self, 
                 dependee: str,
                 depender: str,
                 edge_type: str):
        self.depender = depender
        self.dependee = dependee
        self.edge_type = edge_type


class Dependency(Edge):
    """
      Scanflow relation
    """
    def __init__(self,
                 dependee: str,
                 depender: str,
                 priority: int = 0):
        """
          a relation from dependee to depender, will generate a edge from dependee -> depender
        """
        super(Dependency, self).__init__(dependee=dependee,
           depender=depender, edge_type='dependency')
        self.priority = priority
                    