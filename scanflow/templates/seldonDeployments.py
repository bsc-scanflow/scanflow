from typing import List, Any, OrderedDict
import yaml
from kubernetes.client import V1PodSpec
from scanflow.app import KedaSpec

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class SeldonPodSpec():
    def __init__(self,
                 spec: V1PodSpec = None,
                 kedaSpec: KedaSpec = None):
        self.spec = spec
        self.kedaSpec = kedaSpec

    def to_dict(self):
        seldonPodSpec = {}
        if self.spec:
            seldonPodSpec["spec"] = self.spec.to_dict()
        if self.kedaSpec:
            seldonPodSpec["kedaSpec"] = self.kedaSpec.to_dict()
        
        return seldonPodSpec

class PredictiveUnit():
    def __init__(self,
                 name: str,
                 children = None,
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
        if self.children is None:
            self.children = []
        self.children.append(predictiveUnit)
            
    def to_dict(self):
        graph = {}
        if self.name:
            graph["name"] = self.name
        if self.type:
            graph["type"] = self.type
        if self.implementation:
            graph["implementation"] = self.implementation
        if self.endpoint:
            graph["endpoint"] = self.endpoint
        if self.parameters:
            graph["parameters"] = self.parameters
        if self.modelUri:
            graph["modelUri"] = self.modelUri
        if self.serviceAccountName:
            graph["serviceAccountName"] = self.serviceAccountName
        if self.envSecretRefName:
            graph["envSecretRefName"] = self.envSecretRefName
        
        #children
        graph["children"] = []
        if self.children:
            for predictiveUnit in self.children:
                graph["children"].append(predictiveUnit.to_dict()) 
        
        return graph

class PredictorSpec:
    def __init__(self,
                 name: str,
                 graph: PredictiveUnit,
                 componentSpecs: List[SeldonPodSpec] = None,
                 replicas: int = None,
                 annotation: dict = None,
                 svcOrchSpec = None,
                 explainer = None):
        
        self.name = name
        self.componentSpecs = componentSpecs
        self.graph = graph
        self.replicas = replicas
        self.annotation = annotation
        self.svcOrchSpec = svcOrchSpec
        self.explainer = explainer

    def to_dict(self):
        # - 2.1 predictors
        predictors_spec = {}
        predictors_spec["name"] = self.name
        predictors_spec["replicas"] = self.replicas
        # -- ComponentSpecs
        if self.componentSpecs:
            predictors_spec["componentSpecs"] = []
            for seldonPodSpec in self.componentSpecs:
                predictors_spec["componentSpecs"].append(seldonPodSpec.to_dict())
        # -- Graph
        if self.graph:
            predictors_spec["graph"] = self.graph.to_dict()
        # -- SvcOrchSpec
        if self.svcOrchSpec:
            logging.info("svcOrchSpec is not ready")
        # -- Explainer
        if self.explainer:
            logging.info("explainer is not ready")

        return predictors_spec

class SeldonDeployments:
    def __init__(self, 
                 workflow_name: str, 
                 namespace: str, 
                 replicas: int,
                 predictors: List[PredictorSpec] = None,
                 annotation: dict = None):
        self.name = workflow_name
        self.namespace = namespace
        #seldon deployment spec
        self.replicas = replicas
        self.annotations = annotation
        self.predictors = predictors
        
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
        
        if self.annotations:#(not work now)
            d["spec"]["annotations"] = self.annotations
        
        d["spec"]["predictors"] = []
        for predictor in self.predictors:
            d["spec"]["predictors"].append(predictor.to_dict())
      
        return d

