from pydantic import AnyHttpUrl, BaseSettings, PyObject, BaseModel
from typing import List, Dict
from scanflow.agent.schemas.sensor import SensorCallable

from datetime import datetime

class Settings(BaseSettings):
    AGENT_NAME: str
    AGENT_TYPE: str

    NAMESPACE: str
    SCANFLOW_TRACKER_URI : AnyHttpUrl
    SCANFLOW_TRACKER_LOCAL_URI : AnyHttpUrl
    SCANFLOW_SERVER_URI : AnyHttpUrl

    sensors : Dict[str, SensorCallable] = None
   # {
   #     'tock': {'name': 'tock', 
   #              'func': 'scanflow.agent.template.monitor.custom_sensors.tock',
   #              'trigger': {
   #                  'type': 'interval',
   #                  'seconds': 15
   #                 }
   #             },
   #     'count_number_of_predictions': {
   #               'name': 'count_number_of_predictions',
   #               'func': 'scanflow.agent.template.monitor.custom_sensors.count_number_of_predictions',
   #               'trigger':{
   #                   'type': 'interval',
   #                   'seconds': 30
   #               },
   #               'args':['predictor']
   #             }
   #     }

    class Config:
        case_sensitive = True

settings = Settings()
