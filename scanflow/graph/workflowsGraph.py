
class WorkflowsGraph:
    def __init__(self,
                 workflows):

        self.workflows = workflows
        self.graph = self.generate_graph()

    def generate_graph(self):
        G = nx.Graph()
        G.add_node("scanflow-tracker")
        return  