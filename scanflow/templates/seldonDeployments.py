from typing import List, Any, OrderedDict
import yaml

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ComponentSpec():
    def __init__(self,
                 spec: dict = None,
                 kedaSpec: dict = None):
        self.spec = spec
        self.kedaSpec = kedaSpec

class PredictiveUnit():
    def __init__(self,
                 name: str,
                 children: List[Any] = None,
                 type: str  = None,
                 implementation: str = None,
                 endpoint: dict = None,
                 parameters: dict = None,
                 modelUri: str = None,
                 serviceAccountName: str = None,
                 envSecretRefName: str = None):
        self.name = name
        self.children = children
        self.type = type
        self.implementation = implementation
        self.endpoint = endpoint
        self.parameters = parameters
        self.modelUri = modelUri
        self.serviceAccountName = serviceAccountName
        self.envSecretRefName = envSecretRefName

    def add_children(self, predictiveUnit):
        self.children.append(predictiveUnit)

    def to_dict(self):
        tmp_dict = {}
        service_dict = self.__dict__
        for k,v in service_dict.items():
            if k == 'children' and v is not None:
                children_list = list()
                for children in v:
                    children_list.append(children.to_dict())
                tmp_dict[k] = children_list
            elif v is not None:
                tmp_dict[k] = v
        return tmp_dict


class SeldonDeployments:
    def __init__(self, workflow_name, namespace, replica):
        self.name = workflow_name
        self.namespace = namespace
        self.replica = replica
        self.componentSpecs = []
        self.graph = OrderedDict()
        self.svcOrchSpec = OrderedDict()
        self.explainer = OrderedDict()

    def to_dict(self):
        d = OrderedDict(
            {
                "apiVersion": "machinelearning.seldon.io/v1",
                "kind": "SeldonDeployment",
                "metadata": {},
                "spec": {},
            }
        )

        # 1. d - metadata
        d["metadata"]["name"] = self.name
        d["metadata"]["namespace"] = self.namespace

        # 2. d - spec
        d["spec"]["name"] = self.name
         
        # - 2.1 predictors
        predictors_spec = {}
        predictors_spec["name"] = self.name
        predictors_spec["replica"] = self.replica
        # -- ComponentSpecs
        if self.componentSpecs:
            predictors_spec["componentSpecs"] = self.componentSpecs
        # -- Graph
        if self.graph:
            predictors_spec["graph"] = self.graph
        # -- SvcOrchSpec
        if self.svcOrchSpec:
            logging.info("svcOrchSpec is not ready")
        # -- Explainer
        if self.explainer:
            logging.info("explainer is not ready")

        d["spec"]["predictors"] = []
        d["spec"]["predictors"].append(predictors_spec)

        return d

