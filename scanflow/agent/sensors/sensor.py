from typing import List
from functools import wraps

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(True))

class sensor:
    def __init__(self,
                 executors: List[str],
                 filter_string: str,
                 order_by: str):
        self.executors = executors
        self.filter_string = filter_string
        self.order_by = order_by

    def __call__(self, func):
        @wraps(func)
        async def search_runs(*args, **kwargs):
            print("args"+args[0])
            print(self.executors[0])
            #runs = mlflow.search_runs(["2"])
            #run_ids = runs[0].info.run_id
            print(func.__name__)
            return await func(["1111111","222222","333333"])
        return search_runs