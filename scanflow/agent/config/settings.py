from pydantic import AnyHttpUrl, BaseSettings, PyObject
from typing import List

class Settings(BaseSettings):
    AGENT_NAME: str
    AGENT_TYPE: str

    SCANFLOW_TRACKER_URI : AnyHttpUrl
    SCANFLOW_TRACKER_LOCAL_URI : AnyHttpUrl
    SCANFLOW_SERVER_URI : AnyHttpUrl


    special_function: List[PyObject] = ['scanflow.agent.template.monitor.custom_sensors.sensor_root','math.cos']

    class Config:
        case_sensitive = True

settings = Settings()
