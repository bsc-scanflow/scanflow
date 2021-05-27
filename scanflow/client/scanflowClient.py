import logging
import os

from typing import List, Dict

# scanflow app
from scanflow.app import Executor, Dependency, Workflow, Application, Tracker, Agent, Sensor, IntervalTrigger, DateTrigger, CronTrigger, BaseTrigger

# scanflow graph
#from scanflow.graph import ApplicationGraph


from scanflow.tools.scanflowtools import check_verbosity
from scanflow.server.utils import (
    set_server_uri,
    is_server_uri_set,
    get_server_uri,
)
import requests
import json
import datetime


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ScanflowClient:
    def __init__(self,
                 builder: str = "docker",
                 registry : str = "172.30.0.49:5000",
                 scanflow_server_uri : str = None,
                 verbose=True):
        """
        """
        self.verbose = verbose
        check_verbosity(verbose)
        
        if scanflow_server_uri is not None:
            set_server_uri(scanflow_server_uri)
        if not is_server_uri_set():
            raise ValueError("Scanflow_server_uri is not provided")
        self.scanflow_server_uri = get_server_uri()

        self.builderbackend = self.get_builder(builder, registry)

    def get_builder(self, builder, registry):
        if builder == "docker":
            from scanflow.builder import DockerBuilder
            return DockerBuilder(registry)
        else:
            logging.info(f"unknown builder backend {builder}")

    def build_ScanflowApplication(self,
                                  app: Application, trackerPort: int):
        #build scanflowapp
        return self.builderbackend.build_ScanflowApplication(app, trackerPort)

###   Scanflow graph

#    def draw_ScanflowApplication(self, scanflowapp):
#        appGraph = ApplicationGraph(scanflowapp)
#        return appGraph.draw_graph()

###   Scanflow app
    def ScanflowExecutor(self,
                         name: str,
                         mainfile: str,
                         parameters: dict = None,
                         requirements: str = None,
                         dockerfile: str = None,
                         base_image: str = None,
                         env: str = None):
        return Executor(name, mainfile, parameters, requirements, dockerfile, base_image, env)

    def ScanflowDependency(self,
                         dependee: str,
                         depender: str,
                         priority: int = 0):
        return Dependency(dependee, depender, priority)

    def ScanflowWorkflow(self,
                         name: str,
                         executors: List[Executor],
                         dependencies: List[Dependency],
                         output_dir: str = None):
        return Workflow(name, executors, dependencies, output_dir)


    
    def ScanflowApplication(self,
                            app_name: str,
                            app_dir: str,
                            team_name: str,
                            workflows: List[Workflow]=None,
                            agents: List[Agent]=None,
                            tracker: Tracker = None):
        return Application(app_name, app_dir, team_name, workflows, agents, tracker)

    def ScanflowAgentSensor_IntervalTrigger(self,
                                            weeks: int = 0,
                                            days: int = 0,
                                            hours: int = 0,
                                            minutes: int = 0,
                                            seconds: int = 0,
                                            start_date: str = None,
                                            end_date: str = None,
                                            timezone: str = None,
                                            jitter: int = None):
        return IntervalTrigger(weeks, days, hours, minutes, seconds, start_date, end_date, timezone, jitter)

    def ScanflowAgentSensor_DateTrigger(self,
                                        run_date: str = None,
                                        timezone: str = None):
        return DateTrigger(run_date, timezone)

    def ScanflowAgentSensor_CronTrigger(self,
                                        crontab: str = None):
        return CronTrigger(crontab)

    def ScanflowAgentSensor(self,
                            name: str,
                            isCustom : bool,
                            func_name: str,
                            trigger: BaseTrigger = None,
                            args: tuple = None,
                            kwargs: dict = None,
                            next_run_time: datetime = None):
        return Sensor(name, isCustom, func_name, trigger, args, kwargs, next_run_time)

    def ScanflowAgent(self,
                      name: str,
                      template: str = None,
                      sensors: List[Sensor] = None,
                      dockerfile: str = None,
                      image: str = None):
        return Agent(name, template, sensors, dockerfile, image)

