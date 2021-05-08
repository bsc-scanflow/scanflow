from pydantic import AnyHttpUrl, BaseSettings, PyObject, BaseModel
from typing import List, Dict

class FunctionModel(BaseModel):
    name: str
    path: PyObject

class Settings(BaseSettings):
    AGENT_NAME: str
    AGENT_TYPE: str

    SCANFLOW_TRACKER_URI : AnyHttpUrl
    SCANFLOW_TRACKER_LOCAL_URI : AnyHttpUrl
    SCANFLOW_SERVER_URI : AnyHttpUrl

    sensors : 

    functions : List[FunctionModel] = [{'name':'sensor_root', 'path':'scanflow.agent.template.monitor.custom_sensors.sensor_root'},{"name": "tock","path":"scanflow.agent.template.monitor.custom_sensors.tock"}]

    class Config:
        case_sensitive = True

settings = Settings()
