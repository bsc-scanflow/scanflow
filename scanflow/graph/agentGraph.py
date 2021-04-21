from scanflow.agent import Agent

class AgentGraph:
    def __init__(self,
                 scanflowapp: Agent = None):
    
        self.app = scanflowapp
        self.graph = self.generate_graph()

    def generate_graph(self):
        G = self.app.to_dict()
        return G