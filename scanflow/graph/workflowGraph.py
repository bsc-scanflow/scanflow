from scanflow.app import Workflow

class WorkflowGraph:
    def __init__(self,
                 scanflowapp: Workflow = None):
    
        self.app = scanflowapp
        self.graph = self.generate_graph()

    def generate_graph(self):
        G = self.app.to_dict()
        return G