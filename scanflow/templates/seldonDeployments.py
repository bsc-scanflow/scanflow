from typing import List, Any, OrderedDict
import yaml
from kubernetes.client import V1PodSpec
from scanflow.app import KedaSpec, HpaSpec
from kubernetes.client import V1ResourceRequirements

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#seldonpod -> list[containers]
class SeldonPodSpec():
    def __init__(self,
                 spec: V1PodSpec = None,
                 hpaSpec: HpaSpec = None,
                 kedaSpec: KedaSpec = None,
                 replicas: int = None):
        self.spec = spec
        self.hpaSpec = hpaSpec
        self.kedaSpec = kedaSpec
        self.replicas = replicas

    def to_dict(self):
        seldonPodSpec = {}
        if self.spec:
            seldonPodSpec["spec"] = self.spec.to_dict()
        if self.hpaSpec:
            seldonPodSpec["hpaSpec"] = self.hpaSpec.to_dict()
        if self.kedaSpec:
            if isinstance(self.kedaSpec, KedaSpec):
                seldonPodSpec["kedaSpec"] = self.kedaSpec.to_dict()
            else: 
                seldonPodSpec["kedaSpec"] = self.kedaSpec
        if self.replicas:
            seldonPodSpec["replicas"] = self.replicas
        
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
                 envSecretRefName: str = None,
                 storageInitializerImage: str = None):
        self.name = name
        self.children = children
        self.type = type
        self.implementation = implementation
        self.endpoint = endpoint
        self.parameters = parameters
        self.modelUri = modelUri
        self.serviceAccountName = serviceAccountName
        self.envSecretRefName = envSecretRefName
        self.storageInitializerImage = storageInitializerImage

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
        if self.storageInitializerImage:
            graph["storageInitializerImage"] = self.storageInitializerImage
        
        #children
        graph["children"] = []
        if self.children:
            for predictiveUnit in self.children:
                graph["children"].append(predictiveUnit.to_dict()) 
        
        return graph

# a single application -> several seldon pods(a pod -> a model)
class PredictorSpec:
    def __init__(self,
                 name: str,
                 graph: PredictiveUnit,
                 componentSpecs: List[SeldonPodSpec] = None,
                 replicas: int = None,
                 annotations: dict = None,
                 engineResources:  V1ResourceRequirements = None,
                 svcOrchSpec = None,
                 explainer = None,
                 traffic: int = None,
                 labels: dict = None):
        
        self.name = name
        self.componentSpecs = componentSpecs
        self.graph = graph
        self.replicas = replicas
        self.annotations = annotations
        self.engineResources = engineResources
        self.svcOrchSpec = svcOrchSpec
        self.explainer = explainer
        self.traffic = traffic
        self.labels = labels

    def to_dict(self):
        # - 2.1 predictors
        predictors_spec = {}
        predictors_spec["name"] = self.name
        # -- annotations/labels/replicas/traffic
        if self.annotations:
            predictors_spec["annotations"] = self.annotations
        if self.labels:
            predictors_spec["labels"] = self.labels
        if self.replicas:
            predictors_spec["replicas"] = self.replicas
        if self.traffic:
            predictors_spec["traffic"] = self.traffic   
        # -- ComponentSpecs
        if self.componentSpecs:
            predictors_spec["componentSpecs"] = []
            for seldonPodSpec in self.componentSpecs:
                predictors_spec["componentSpecs"].append(seldonPodSpec.to_dict())
        # -- Graph
        if self.graph:
            predictors_spec["graph"] = self.graph.to_dict()
        # -- engineResources
        if self.engineResources:
            predictors_spec["engineResources"] = self.engineResources.to_dict()
        # -- SvcOrchSpec
        if self.svcOrchSpec:
            logging.info("svcOrchSpec is not ready")
        # -- Explainer
        if self.explainer:
            logging.info("explainer is not ready")

        return predictors_spec

#https://docs.seldon.io/projects/seldon-core/en/latest/reference/seldon-deployment.html?highlight=crd%20deployment
class SeldonDeployments:
    def __init__(self, 
                 workflow_name: str, 
                 namespace: str, 
                 replicas: int,
                 predictors: List[PredictorSpec] = None,
                 annotations: dict = None):
        self.name = workflow_name
        self.namespace = namespace
        #seldon deployment spec
        self.replicas = replicas
        self.annotations = annotations
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
        
        if self.annotations:
            d["spec"]["annotations"] = self.annotations
        
        d["spec"]["predictors"] = []
        for predictor in self.predictors:
            d["spec"]["predictors"].append(predictor.to_dict())
      
        return d

#seldondeployment -> list[Predictors](different k8s services) -> List[Component](scanflow service, graph to define dependency)
