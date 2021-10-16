from kubernetes.client import V1ResourceRequirements, V1Affinity
from typing import List

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class Node():
    """
        Abstract base Node class.

    """
    def __init__(self, name: str, node_type: str):
        self.name = name
        self.node_type = node_type

class Executor(Node):
    """
        Minimal unit of execution.

    """
    def __init__(self,
                 name: str,
                 mainfile: str,
                 parameters: dict = None,
                 requirements: str = None,
                 dockerfile: str = None,
                 base_image: str = None,
                 env: dict = None,
                 image: str = None,
                 timeout: int = None,
                 resources: V1ResourceRequirements = None,
                 affinity: V1Affinity = None):

        super(Executor, self).__init__(name=name, node_type='executor')
        self.mainfile = mainfile
        self.parameters = parameters
        self.requirements = requirements
        self.dockerfile = dockerfile
        self.base_image = base_image
        self.env = env
        self.image = image
        self.timeout = timeout
        self.resources = resources
        self.affinity = affinity

    def to_dict(self):
        tmp_dict = {}
        executor_dict = self.__dict__
        # api = ApiClient()
        for k, v in executor_dict.items():
            if k == 'resources' and v is not None:
                tmp_dict[k] = v.to_dict()
            elif k == 'affinity' and v is not None:
                tmp_dict[k] = v.to_dict()
            else:
                tmp_dict[k] = v
        
        # logging.info(f"executor {self.name}: {tmp_dict}")
        return tmp_dict


#    @property
#    def image(self):
#        return self.__image
#
#    @image.setter
#    def image(self,
#              image: str):
#        self.__image = image

class Service(Node):
    """
        Minimal unit of service.

    """
    def __init__(self,
                 name: str,
                 mainfile: str = None,
                 image: str = None,
                 env: dict = None,
                 envfrom: dict = None,
                 requirements: str = None,
                 dockerfile: str = None,
                 base_image: str = None,
                 service_type: str = None,
                 implementation_type: str = None,
                 modelUri: str = None,
                 envSecretRefName: str = None,
                 endpoint: dict = None,
                 parameters: List[dict] = None,
                 resources: V1ResourceRequirements = None,
                 affinity: V1Affinity = None):
        super(Service, self).__init__(name=name, node_type='service')
        
        self.image = image
        self.env = env
        self.envfrom = envfrom
        self.mainfile = mainfile
        #build
        self.requirements = requirements
        self.dockerfile = dockerfile
        self.base_image = base_image
        #1. componentSpecs:spec:containers

        #2. graph
        #MODEL, TRANSFORMER, COMBINER, ROUTER, OUTPUT_TRANSFORMER
        self.service_type = service_type
        #SIMPLE_MODEL, SIMPLE_ROUTER, RANDOM_ABTEST, AVERAGE_COMBINER, 
        #TENSORFLOW_SERVER, MLFLOW_SERVER, SKELEARN_SERVER, XGBOOST_SERVER
        self.implementation_type = implementation_type
        self.modelUri = modelUri
        self.envSecretRefName = envSecretRefName
        self.endpoint = endpoint
        self.parameters = parameters
        self.resources = resources
        self.affinity = affinity

    def to_dict(self):
        tmp_dict = {}
        service_dict = self.__dict__
        for k, v in service_dict.items():
            if k == 'resources' and v is not None:
                tmp_dict[k] = v.to_dict()
            elif k == 'affinity' and v is not None:
                tmp_dict[k] = v.to_dict()
            else:
                tmp_dict[k] = v
        return tmp_dict