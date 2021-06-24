from typing import List, Dict

from scanflow.app import Node
from scanflow.app import Edge
from scanflow.app import KedaSpec

from kubernetes.client import V1Affinity

class Workflow(object):
    def __init__(self,
                 name: str,
                 nodes: List[Node],
                 edges: List[Edge] = None,
                 affinity: V1Affinity = None,
                 kedaSpec: KedaSpec = None,
                 output_dir: str = None):

        self.name = name
        self.nodes = nodes
        self.edges = edges
        self.affinity = affinity
        self.kedaSpec = kedaSpec
        self.output_dir = output_dir

    def to_dict(self):
        tmp_dict = {}
        workflow_dict = self.__dict__
        for k,v in workflow_dict.items():
            if k == 'nodes':
                nodes_list = list()
                for node in v:
                    nodes_list.append(node.__dict__)
                tmp_dict[k] = nodes_list
            elif k == 'edges' and v is not None:
                edges_list = list()
                for edge in v:
                    edges_list.append(edge.__dict__)
                tmp_dict[k] = edges_list
            #elif k == 'kedaSpec' and v is not None:
            #    tmp_dict[k] = v.to_dict()
            else:
                tmp_dict[k] = v
        return tmp_dict
            