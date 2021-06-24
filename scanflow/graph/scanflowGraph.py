## graph for scanflow local tracker

class ScanflowGraph:
    def __init__(self,
                 tracker):
    
        self.tracker = tracker
        self.graph = self.generate_graph()

    def generate_graph(self):
        G = nx.Graph()
        G.add_node("scanflow-tracker")
        return G