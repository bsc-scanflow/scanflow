from typing import List, Dict
import logging

from scanflow.app import Node
from scanflow.app import Edge
from scanflow.app import KedaSpec

from kubernetes.client import V1Affinity, V1ResourceRequirements

from scanflow.app.workflow.scaler import HpaSpec

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class Workflow(object):
    def __init__(self,
                 name: str,
                 nodes: List[Node],
                 edges: List[Edge] = None,
                 type: str = None,
                 resources: V1ResourceRequirements = None,
                 affinity: V1Affinity = None,
                 kedaSpec: KedaSpec = None,
                 hpaSpec: HpaSpec = None,
                 output_dir: str = None):

        self.name = name
        self.nodes = nodes
        self.edges = edges
        self.type = type #batch or online
        self.resources = resources
        self.affinity = affinity
        self.kedaSpec = kedaSpec
        self.hpaSpec = hpaSpec
        self.output_dir = output_dir

    def to_dict(self):
        tmp_dict = {}
        workflow_dict = self.__dict__
        for k,v in workflow_dict.items():
            if k == 'nodes':
                nodes_list = list()
                for node in v:
                    # nodes_list.append(node.__dict__)
                    nodes_list.append(node.to_dict())
                tmp_dict[k] = nodes_list
            elif k == 'edges' and v is not None:
                edges_list = list()
                for edge in v:
                    edges_list.append(edge.__dict__)
                tmp_dict[k] = edges_list
            elif k == 'resources' and v is not None:
                tmp_dict[k] = v.to_dict()
            elif k == 'affinity' and v is not None:
                tmp_dict[k] = v.to_dict()
            elif k == 'kedaSpec' and v is not None:
                tmp_dict[k] = v.to_dict()
            elif k == 'hpaSpec' and v is not None:
                tmp_dict[k] = v.to_dict()
            else:
                tmp_dict[k] = v

        logging.info(f"workflow {self.name}: {tmp_dict}")
        return tmp_dict
            