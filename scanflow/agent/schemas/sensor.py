from pydantic import BaseModel, Field
from typing import Optional, List, Dict

import time

class Sensor(BaseModel):
    name: str
    func: PyObject
    args: tuple = None
    kwargs: tuple = None
    next_run_time: str = None

class SensorOutput(Sensor):
    id: str 
    func_name: str
    trigger: str

class BaseTrigger(BaseModel):
    pass

class IntervalTrigger(BaseTrigger):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 120
    start_date: str = None
    end_date: str = None
    timezone: str = None
    jitter: int = None
    
class DateTrigger(BaseTrigger):
    run_date: str = None
    timezone: str = None

class CronTrigger(BaseTrigger):
    crontab: str