from pydantic import BaseModel, Field, PyObject
from typing import Optional, List, Dict
from datetime import datetime

class BaseTrigger(BaseModel):
    base: str = None

class IntervalTrigger(BaseTrigger):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    start_date: str = None
    end_date: str = None
    timezone: str = None
    jitter: int = None
    
class DateTrigger(BaseTrigger):
    run_date: str = None
    timezone: str = None

class CronTrigger(BaseTrigger):
    crontab: str = None

class Sensor(BaseModel):
    name: str
    trigger: BaseTrigger = None
    args: tuple = None
    kwargs: tuple = None
    next_run_time: datetime = None

class SensorCallable(Sensor):
    func: PyObject

class SensorOutput(Sensor):
    id: str 
    func_name: str
    trigger_str: str