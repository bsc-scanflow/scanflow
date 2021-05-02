
class AgentsGraph:
    def __init__(self,
                 agents):
        self.agents = agents
        self.graph = self.generate_graph()

    def generate_graph(self):
        G = nx.Graph()
        G.add_node("scanflow-tracker")
        return G