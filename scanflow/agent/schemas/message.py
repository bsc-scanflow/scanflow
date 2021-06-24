from pydantic import BaseModel, Field, PyObject, AnyHttpUrl
from typing import Optional, List, Dict

class Message(BaseModel):
    type: str
    function: str

class SensorMessage(Message):
    #sensor: f"{type}: call {function} from {nodes} -- the result is {value}"
    nodes: List[str] = None 
    value: str = None
    client: tuple = None
    server: tuple = None

class ActuatorMessage(Message):
    #actuator: f"{type}: call {function} -- make call to {depender}:{url}, {status}"
    depender: str
    url: AnyHttpUrl
    status: int
    detail: str