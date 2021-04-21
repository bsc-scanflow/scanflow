## graph for scanflow local tracker
from scanflow.tracker import Tracker

class ScanflowGraph:
    def __init__(self,
                 scanflowapp: Tracker = None):
    
        self.app = scanflowapp
        self.graph = self.generate_graph()

    def generate_graph(self):
        G = self.app.to_dict()
        return G