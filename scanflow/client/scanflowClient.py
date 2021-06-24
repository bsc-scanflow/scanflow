import logging
import os

from typing import List, Dict

# scanflow app
from scanflow.app import Executor, Service, Node
from scanflow.app import Edge, Dependency
from scanflow.app import Agent, Sensor, IntervalTrigger, DateTrigger, CronTrigger, BaseTrigger
from scanflow.app import Workflow, Application, Tracker
from scanflow.app import KedaSpec

# kubernetes
from kubernetes.client import V1Affinity, V1NodeAffinity, V1PodAffinity, V1PodAntiAffinity
from kubernetes.client import V1LabelSelectorRequirement, V1NodeSelectorTerm, V1PreferredSchedulingTerm, V1NodeSelector, V1LabelSelectorRequirement, V1WeightedPodAffinityTerm
from kubernetes.client import V1PodAffinityTerm
from kubernetes.client import V1ResourceRequirements


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
                         env: str = None,
                         resources: V1ResourceRequirements = None):
        return Executor(name, mainfile, parameters, requirements, 
        dockerfile, base_image, env, resources=resources)

    def ScanflowService(self,
                        name: str,
                        mainfile: str = None,
                        image: str = None,
                        env: dict = None,
                        envfrom: dict = None,
                        requirements: str = None,
                        dockerfile: str = None,
                        base_image: str = None,
                        service_type: str = None,
                        implementation_type: str = None,
                        modelUri: str = None,
                        envSecretRefName: str = None,
                        endpoint: dict = None,
                        parameters: List[dict] = None,
                        resources: V1ResourceRequirements = None):
        return Service(name, mainfile, image, env, envfrom, 
        requirements, dockerfile, base_image, service_type, 
        implementation_type, modelUri, envSecretRefName, endpoint, 
        parameters, resources)

    def ScanflowDependency(self,
                         dependee: str,
                         depender: str,
                         priority: int = 0):
        return Dependency(dependee, depender, priority)

    def ScanflowWorkflow(self,
                         name: str,
                         nodes: List[Node],
                         edges: List[Edge] = None,
                         affinity: V1Affinity = None,
                         kedaSpec: KedaSpec = None,
                         output_dir: str = None):
        return Workflow(name, nodes, edges, affinity, kedaSpec, output_dir)
    
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


#resources
    def V1ResourceRequirements(self,
                               requests: dict = None,
                               limits: dict = None):
        return V1ResourceRequirements(limits=limit, requests=requests)

#affinity
    def V1Affinity(self,
                   node_affinity: V1NodeAffinity = None,
                   pod_affinity: V1PodAffinity = None,
                   pod_anti_affinity: V1PodAntiAffinity = None):
        return V1Affinity(node_affinity=node_affinity, 
                          pod_affinity=pod_affinity,
                          pod_anti_affinity=pod_anti_affinity)
        #TODO: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Affinity.md    

    def V1PodAntiAffinity(self,
                 preferred_during_scheduling_ignored_during_execution: List[V1WeightedPodAffinityTerm] = None,
		         required_during_scheduling_ignored_during_execution: List[V1PodAffinityTerm] = None):
        return V1PodAntiAffinity(
            preferred_during_scheduling_ignored_during_execution=preferred_during_scheduling_ignored_during_execution,
            required_during_scheduling_ignored_during_execution=required_during_scheduling_ignored_during_execution)

    def V1PodAffinity(self,
                 preferred_during_scheduling_ignored_during_execution: List[V1WeightedPodAffinityTerm] = None,
		         required_during_scheduling_ignored_during_execution: List[V1PodAffinityTerm] = None):
        return V1PodAffinity(
            preferred_during_scheduling_ignored_during_execution=preferred_during_scheduling_ignored_during_execution,
            required_during_scheduling_ignored_during_execution=required_during_scheduling_ignored_during_execution
        )

    def V1NodeAffinity(self,
                 preferred_during_scheduling_ignored_during_execution: List[V1PreferredSchedulingTerm] = None,
		         required_during_scheduling_ignored_during_execution: V1NodeSelector = None):
        return V1NodeAffinity(preferred_during_scheduling_ignored_during_execution=preferred_during_scheduling_ignored_during_execution,
        required_during_scheduling_ignored_during_execution=required_during_scheduling_ignored_during_execution)

    def V1NodeSelectorRequiement(self,
                 key: str,
       		     operator: str,
       		     values: List[str] = None):
        """
       	:params: values: An array of string values. 
       	If the operator is In or NotIn, the values array must be non-empty. 
       	If the operator is Exists or DoesNotExist, the values array must be empty. 
       	If the operator is Gt or Lt, the values array must have a single element, which will be interpreted as an integer. 
       	This array is replaced during a strategic merge patch.
       	"""
        return V1NodeSelectorRequiement(key, operator, values)


    def V1NodeSelectorTerm(self,
                 match_expressions: List[V1NodeSelectorRequiement]=None,
		         match_fields: List[V1NodeSelectorRequiement]=None):
        return V1NodeSelectorTerm(match_expressions=match_expressions,
        match_fields=match_fields)

    def V1PreferredSchedulingTerm(self,
                 preference: V1NodeSelectorTerm,
		         weight: int):
        return V1PreferredSchedulingTerm(preference=preference,weight=weight)

    def V1NodeSelector(self,
                 node_selector_terms: List[V1NodeSelectorTerm]):
        return V1NodeSelector(node_selector_terms=node_selector_terms)

    def V1LabelSelectorRequirement(self,
                 key: str,
		         operator: str,
		         values: List[str] = None):
        """
     	:params: values: An array of string values. 
     	If the operator is In or NotIn, the values array must be non-empty. 
     	If the operator is Exists or DoesNotExist, the values array must be empty. 
     	This array is replaced during a strategic merge patch.
	    """
        return V1LabelSelectorRequirement(key, operator, values)

    def V1LabelSelector(self,
                 match_expressions: List[V1LabelSelectorRequirement] = None,
		         match_labels: dict = None):
        return V1LabelSelector(match_expressions,match_labels)

    def V1PodAffinityTerm(self,
                 topology_key: str,
                 label_selector: V1LabelSelector,
		         namespaces: List[str]):
        return V1PodAffinityTerm(topology_key, label_selector, namespaces)

    def V1WeightedPodAffinityTerm(self,
                pod_affinity_term: V1PodAffinityTerm,
		        weight: int):
        return V1WeightedPodAffinityTerm(pod_affinity_term, weight)