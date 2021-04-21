import networkx as nx
import matplotlib.pyplot as plt
import logging

from scanflow.tools.scanflowtools import check_verbosity

from scanflow.app import Application
from scanflow.graph import WorkflowGraph
from scanflow.graph import ScanflowGraph

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ApplicationGraphs:
    def __init__(self,
                 scanflowapp: Application = None,
                 scanflowapp_meta: str = None,
                 verbose = False):
        self.verbose = verbose
        check_verbosity(verbose)
        
        if scanflowapp is not None:
            logging.error(f"use scanflowapp to generate graphs")
            self.app = scanflowapp.to_dict()
            self.graphs = self.generate_graphs()
        elif scanflowapp_meta is not None:
            logging.error(f"use scanflowapp_meta to generate graphs")
            self.app = scanflowapp_meta
            self.graphs = self.generate_graphs()
        else:
            logging.error(f"must provide scanflow app or scanflow app metadata")

    def generate_graphs(self):
        graphs = list()
        if self.app['workflows'] is not None:
            for workflow in self.app['workflows']:
                G = self.generte_DiGraph(workflow)
                graphs.append(G) 
        if self.app['agents'] is not None:
            for agent in self.app['agents']:
                G = self.generate_Graph(agent)
                graphs.append(G)
    
    def generate_WorkflowGraph(self, workflow):
        G = nx.DiGraph()


    def generate_AgentGraph(self, agent):

    def generate_ScanflowGraph(self,)
    
    def draw_graphs(self):
        graphsName = f"{self.app['app_name']}-{self.app['team_name']}"
        graph = 
