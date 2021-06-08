from typing import Optional, List

class ScaleTrigger():
    def __init__(self,
                 type: str,
                 metadata: dict):
        self.type = type
        self.metadata = metadata

class ScaleTriggerPrometheus(ScaleTrigger):
    def __init__(self,
                 serverAddress: str,
                 metricName: str,
                 query: str,
                 threshold: int):
        super(ScaleTriggerPrometheus, self).__init__(type="prometheus")
        self.serverAddress = serverAddress
        self.metricName = metricName
        self.query = query
        self.threshold = threshold
        self.metadata = __dict__


class KedaSpec():
    def __init__(self,
                 triggers: List[ScaleTrigger],
                 pollingInterval: Optional[int],
                 cooldownPeriod: Optional[int],
                 minReplicaCount: Optional[int],
                 maxReplicaCount: Optional[int]):
        """
        default
           pollingInterval: 30s
           cooldownPeriod: 30s
           minReplicaCount: 0
           maxReplicaCount: 100
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



