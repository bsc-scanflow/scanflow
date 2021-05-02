import networkx as nx
import logging

from scanflow.app import Application
from scanflow.graph import WorkflowsGraph, AgentsGraph,ScanflowGraph

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ApplicationGraph:
    def __init__(self,
                 scanflowapp):
        
        if isinstance(scanflowapp, Application):
            logging.error(f"use scanflowapp to generate graphs")
            self.app = scanflowapp.to_dict()
            self.graphs = self.generate_graphs()
        elif isinstance(scanflowapp, dict):
            logging.error(f"use scanflowapp_meta to generate graphs")
            self.app = scanflowapp
            self.graphs = self.generate_graphs()
        else:
            logging.error(f"must provide scanflow app or scanflow app metadata")

    def generate_graphs(self):
        graphs = list()
#        if self.app['workflows'] is not None:
#            workflowsGraph = WorkflowsGraph(self.app['workflows'])
#            graphs.append(workflowsGraph.graph) 
#        if self.app['agents'] is not None:
#            agentsGraph = AgentsGraph(self.app['agents'])
#            graphs.append(agentsGraph.graph) 
        if self.app['tracker'] is not None:
            scanflowGraph = ScanflowGraph(self.app['tracker'])
            graphs.append(scanflowGraph.graph)


    def draw_graphs(self):
        import matplotlib.pyplot as plt

        graphsName = f"{self.app['app_name']}-{self.app['team_name']}"

#        G = nx.DiGraph(directed=True)
#
#        edges_with_parent = [(d['data']['parent'], d['data']['id'])
#                  for d in graph if 'parent' in d['data'].keys()]
#        parent_nodes = {edge[0]:'blue' for edge in edges_with_parent}
#        # color_map = ['blue' for e in edges]
#        edges_rest = [(d['data']['source'], d['data']['target'])
#                  for d in graph if 'source' in d['data'].keys()]
#    
#        rest_nodes = {edge:'cyan' for edge in list(set(list(sum(edges_rest, ()))))}
#    
#        total_edges = edges_with_parent + edges_rest
#    
#        G.add_edges_from(total_edges)
    
    #     plt.title('Topology')
#        pos = nx.spectral_layout(G)
#        color_nodes = {**parent_nodes, **rest_nodes}
#        color_map = [color_nodes[node] for node in G.nodes()]
        fig = plt.figure()
        fig.add_subplot(1, 1, 1)
        plt.title("Workflow")
        nx.draw(G, pos,  with_labels = True, arrows=True)
        plt.show()
    