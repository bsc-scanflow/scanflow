from typing import List, Dict
import logging

from scanflow.app import Sensor

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)
class Agent:
    def __init__(self,
                 name: str,
                 template: str = None,
                 sensors: List[Sensor] = None,
                 dockerfile: str = None,
                 image: str = None):
        """
           we provide several templates. the functions within the templates need to be used together with the agent file.
           user can also define their own type of agent
        """
        
        self.name = name
        self.template = template
        self.sensors = sensors
        self.dockerfile = dockerfile
        self.image = image

    def to_dict(self):
        tmp_dict = {}
        agent_dict = self.__dict__
        for k, v in agent_dict.items():
            if k == 'sensors' and v is not None:
                sensors_list = list()
                for sensor in v:
                    sensors_list.append(sensor.to_dict())
                tmp_dict[k] = sensors_list
            else:
                tmp_dict[k] = v

        logging.info(f"Scanflowagent-{self.name}: {tmp_dict}")
        return tmp_dict
        
