from typing import List, Dict
import time
from datetime import datetime

class BaseTrigger():
    def __init__(self):
        pass

class IntervalTrigger(BaseTrigger):
    def __init__(self,
                 weeks: int = 0,
                 days: int = 0,
                 hours: int = 0,
                 minutes: int = 0,
                 seconds: int = 0,
                 start_date: str = None,
                 end_date: str = None,
                 timezone: str = None,
                 jitter: int = None):
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.start_date = start_date
        self.end_date = end_date
        self.timezone = timezone
        self.jitter = jitter

class DateTrigger(BaseTrigger):
    def __init__(self,
                 run_date: str = None,
                 timezone: str = None):
        self.run_date = run_date
        self.timezone = timezone

class CronTrigger(BaseTrigger):
    def __init__(self,
                 crontab: str = None):
        self.crontab = crontab

class Sensor():
    def __init__(self,
                 name: str,
                 isCustom : bool,
                 func_name: str,
                 trigger: BaseTrigger = None,
                 args: tuple = None,
                 kwargs: dict = None,
                 next_run_time: datetime = None):
        self.name = name
        self.isCustom = isCustom
        self.func_name = func_name
        self.trigger = trigger
        self.args = args
        self.kwargs = kwargs
        self.next_run_time = next_run_time

    def add_trigger(self,
                    trigger: BaseTrigger):
        self.trigger = trigger

    def to_dict(self):
        tmp_dict = {}
        sensor_dict = self.__dict__
        for k, v in sensor_dict.items():
            if k == 'trigger' and v is not None:
                tmp_dict[k] = v.__dict__
            elif k == 'next_run_time' and v is not None:
                tmp_dict[k] = v.isoformat()
            else:
                tmp_dict[k] = v
        return tmp_dict
