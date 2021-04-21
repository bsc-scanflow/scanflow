from typing import List, Dict

from scanflow.app import Executor
from scanflow.app import Dependency


class Workflow(object):
    def __init__(self,
                 name: str = None,
                 executors: List[Executor] = None,
                 dependencies: List[Dependency] = None):

        self.name = name
        self.executors = executors
        self.dependencies = dependencies

    def to_dict(self):
        tmp_dict = {}
        workflow_dict = self.__dict__
        for k,v in workflow_dict.items():
            if k == 'executors':
                executors_list = list()
                for executor in v:
                    executors_list.append(executor.__dict__)
                tmp_dict[k] = executors_list
            elif k == 'dependencies':
                dependencies_list = list()
                for dependency in v:
                    dependencies_list.append(dependency.__dict__)
                tmp_dict[k] = dependencies_list
            else:
                tmp_dict[k] = v
        return tmp_dict
            