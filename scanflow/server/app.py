from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class Executor(BaseModel):
    name: str 
    image: str
    mainfile: Optional[str] = None
    parameter: Optional[dict] = None
    requirements: Optional[str] = None
    dockerfile: Optional[str] = None
    env: Optional[str] = None

class Dependency(BaseModel):
    dependee: str
    depender: str
    priority: Optional[int] = 0


class Workflow(BaseModel):
    name: str 
    executors: List[Executor] 
    dependencies: List[Dependency]

class Agent(BaseModel):
    name: str
    image: str
    template: Optional[str] = None
    mainfile: Optional[str] = None
    parameters: Optional[dict] = None

class Application(BaseModel):
    app_name: str 
    app_dir: str 
    team_name: str 
    workflows: Optional[List[Workflow]] = None
    agents: Optional[List[Agent]] = None

