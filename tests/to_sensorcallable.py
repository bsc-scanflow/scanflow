import sys
import os
sys.path.insert(0,'..')

import scanflow
from scanflow.client import ScanflowClient

client = ScanflowClient(verbose=True)
from datetime import datetime

math = __import__(math)
print(math.cos(0))
#print(type(datetime))

trigger = client.ScanflowAgentSensor_IntervalTrigger(hours=1)
sensor = client.ScanflowAgentSensor(name='count_number_of_predictions',
                                    isCustom=True,
                                    func_name='count_number_of_predictions',
                                    trigger=trigger,
                                    args=("args"),
                                    kwargs={"kwargs":"kwargs"},
                                    next_run_time=datetime.now())
tracker = client.ScanflowAgent(name='tracker',
                              template='monitor',
                              sensors=[sensor])

a = {}
name = "namestring"
sensor1 = {"tick":{f"{name}": "peini","age":20}}
sensor2 = {"tock":{"name": "jie","age":20}}
a.update(sensor1)
a.update(sensor2)
print(a)

print(sensor.to_dict())
import json
print(json.dumps(sensor.to_dict()))
print(sensor._to_SensorCallable_dict())
