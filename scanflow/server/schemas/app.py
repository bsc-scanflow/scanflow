from pydantic import BaseModel, Field, Extra, validator
from typing import Optional, List, Dict, Union, Literal

class Node(BaseModel):
    name: str
    node_type: str
    image: str
    mainfile: Optional[str] = None
    parameters: Optional[dict] = None
    requirements: Optional[str] = None
    dockerfile: Optional[str] = None
    base_image: Optional[str] = None
    env: Optional[str] = None

class Executor(BaseModel):
    name: str
    node_type: str
    image: str
    mainfile: Optional[str] = None
    parameters: Optional[dict] = None
    requirements: Optional[str] = None
    dockerfile: Optional[str] = None
    base_image: Optional[str] = None
    env: Optional[str] = None

class Service(BaseModel):
    name: str
    node_type: str

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
    edges: List[Edge] = None
    output_dir: Optional[str] = None

class Agent(BaseModel):
    name: str
    image: str
    template: Optional[str] = None
    mainfile: Optional[str] = None
    parameters: Optional[dict] = None


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

