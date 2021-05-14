from pydantic import BaseModel, Field, PyObject
from typing import Optional, List, Dict, Any
from datetime import datetime

class Trigger(BaseModel):
    type: str = None
    #1.interval
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    start_date: str = None
    end_date: str = None
    timezone: str = None
    jitter: int = None
    #2.date
    run_date: str = None
    timezone: str = None
    #3.crontab
    crontab: str = None

class Sensor(BaseModel):
    name: str
    trigger: Trigger = None
    args: tuple = None
    kwargs: Dict[str, Any] = None
    next_run_time: datetime = None

class SensorCallable(Sensor):
    func: PyObject

class SensorOutput(BaseModel):
    id: str 
    name: str
    func_name: str
    trigger_str: str
    next_run_time: datetime = None