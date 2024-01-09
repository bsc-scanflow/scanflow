from typing import Optional, List
from kubernetes.client import V2MetricSpec

class ScalerTrigger():
    def __init__(self,
                 type: str,
                 metadata: dict):
        self.type = type
        self.metadata = metadata

class ScalerTriggerPrometheusMetadata():
    def __init__(self,
                 serverAddress: str,
                 metricName: str,
                 query: str,
                 threshold: str):
        self.serverAddress = serverAddress
        self.metricName = metricName
        self.query = query
        self.threshold = threshold


class KedaSpec():
    def __init__(self,
                 triggers: List[ScalerTrigger],
                 pollingInterval: Optional[int],
                 cooldownPeriod: Optional[int],
                 minReplicaCount: Optional[int],
                 maxReplicaCount: Optional[int]):
        """
        default
           pollingInterval: 30s
           cooldownPeriod: 30s
           minReplicaCount: 0
           maxReplicaCount: 10
        """
        self.triggers = triggers
        self.pollingInterval = pollingInterval
        self.cooldownPeriod = cooldownPeriod
        self.minReplicaCount = minReplicaCount
        self.maxReplicaCount = maxReplicaCount

    def to_dict(self):
        tmp_dict = {}
        keda_dict = self.__dict__
        for k,v in keda_dict.items():
            if k == 'triggers':
                trigger_list = list()
                for trigger in v:
                    trigger_list.append(trigger.__dict__)
                tmp_dict[k] = trigger_list
            else:
                tmp_dict[k] = v
        return tmp_dict  
class HpaSpec():
    def __init__(self,
                 minReplica: Optional[int],
                 maxReplica: Optional[int],
                 metrics: List[V2MetricSpec]):
        """
        default
           minreplica:
           maxreplica: 
           metrics: autoscaling
        """
        self.metrics = metrics
        self.minReplica = minReplica
        self.maxReplica = maxReplica

    def to_dict(self):
        tmp_dict = {}
        hpa_dict = self.__dict__
        for k,v in hpa_dict.items():
            if k == 'metrics':
                metrics_list = list()
                for metric in v:
                    metrics_list.append(metric.__dict__)
                tmp_dict[k] = metrics_list
            else:
                tmp_dict[k] = v
        return tmp_dict  


