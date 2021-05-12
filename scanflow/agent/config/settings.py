from pydantic import AnyHttpUrl, BaseSettings, PyObject, BaseModel
from typing import List, Dict
from scanflow.agent.schemas.sensor import SensorCallable
from scanflow.agent.schemas.rule import Rule
from scanflow.agent.schemas.actuator import Actuator

from datetime import datetime

class Settings(BaseSettings):
    AGENT_NAME: str
    AGENT_TYPE: str

    SCANFLOW_TRACKER_URI : AnyHttpUrl
    SCANFLOW_TRACKER_LOCAL_URI : AnyHttpUrl
    SCANFLOW_SERVER_URI : AnyHttpUrl

    sensors : Dict[str, SensorCallable] = {
        'tock': {'name': 'tock', 
                 'func': 'scanflow.agent.template.monitor.custom_sensors.tock',
                 'trigger': {
                     'type': 'interval',
                     'seconds': 15
                    }
                },
        'count_number_of_predictions': {
                  'name': 'count_number_of_predictions',
                  'func': 'scanflow.agent.template.monitor.custom_sensors.count_number_of_predictions',
                  'trigger':{
                      'type': 'interval',
                      'seconds': 30
                  },
                  'args':['predictor']
                }
        }
    rules: Dict[str, Rule] = None
    actuators: Dict[str, Actuator] = None

    dependencies: Dict[str, AnyHttpUrl] = None

    class Config:
        case_sensitive = True

settings = Settings()
