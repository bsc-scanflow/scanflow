from pydantic import BaseModel, Field, Extra, validator
from typing import Optional, List, Dict, Union, Literal, Any

from scanflow.agent.schemas.sensor import Trigger
from datetime import datetime

#scaler
#class ScalerTrigger(BaseModel):
#    type: str
#    metadata: dict
#class KedaSpec(BaseModel):
#    triggers: List[ScalerTrigger]
#    pollingInterval: Optional[int]
#    cooldownPeriod: Optional[int]
#    minReplicaCount: Optional[int]
#    maxReplicaCount: Optional[int]
    
#affinity


class Node(BaseModel):
    name: str
    node_type: str
    image: Optional[str] = None
    mainfile: Optional[str] = None
    parameters: Any = None
    requirements: Optional[str] = None
    dockerfile: Optional[str] = None
    base_image: Optional[str] = None
    env: Optional[dict] = None
    timeout: Optional[int] = 7200
    resources: Optional[dict] = None
    affinity: Optional[dict] = None

    env: Optional[dict] = None
    envfrom: Optional[dict] = None
    service_type: Optional[str] = None
    implementation_type: Optional[str] = None
    modelUri: Optional[str] = None
    envSecretRefName: Optional[str] = None
    endpoint: Optional[dict] = None


class Executor(BaseModel):
    name: str
    node_type: str
    image: str
    mainfile: Optional[str] = None
    parameters: Optional[dict] = None
    requirements: Optional[str] = None
    dockerfile: Optional[str] = None
    base_image: Optional[str] = None
    env: Optional[dict] = None
    timeout: Optional[int] = 7200
    resources: Optional[dict] = None
    affinity: Optional[dict] = None

class Service(BaseModel):
    name: str
    node_type: str
    image: Optional[str] = None
    env: Optional[dict] = None
    envfrom: Optional[dict] = None
    requirements: Optional[dict] = None
    dockerfile: Optional[str] = None
    base_image: Optional[str] = None
    service_type: Optional[str] = None
    implementation_type: Optional[str] = None
    modelUri: Optional[str] = None
    envSecretRefName: Optional[str] = None
    endpoint: Optional[dict] = None
    parameters: Optional[List[dict]] = None
    resources: Optional[dict] = None
    affinity: Optional[dict] = None


class Edge(BaseModel):
    dependee: str
    depender: str
    edge_type: str
    priority: Optional[int] = 0

class Dependency(BaseModel):
    dependee: str
    depender: str
    edge_type: str
    priority: Optional[int] = 0

class Workflow(BaseModel):
    name: str 
    nodes: List[Node] = None
    edges: Optional[List[Edge]] = None
    type: Optional[str] = None
    resources: Optional[dict] = None
    affinity: Optional[dict] = None
    kedaSpec: Optional[dict] = None
    hpaSpec: Optional[dict] = None
    output_dir: Optional[str] = None


class Sensor(BaseModel):
    name: str
    isCustom : bool
    func_name: str
    trigger: Trigger = None
    args: tuple = None
    kwargs: dict = None
    next_run_time: datetime = None
class Agent(BaseModel):
    name: str
    image: str
    template: Optional[str] = None
    dockerfile: Optional[str] = None
    sensors: Optional[List[Sensor]] = None

class Tracker(BaseModel):
    nodePort: int
    image: str

class Application(BaseModel):
    app_name: str 
    app_dir: str 
    team_name: str 
    workflows: Optional[List[Workflow]] = None
    agents: Optional[List[Agent]] = None
    tracker: Optional[Tracker] = None

