from typing import List, Optional
from functools import wraps

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)

class sensor:
    def __init__(self,
                 executors: List[str],
                 filter_string: str = '', 
                 order_by: Optional[List[str]] = None):
        self.executors = executors
        # default search all runs
        self.filter_string = filter_string
        self.order_by = order_by

    def __call__(self, func):
        @wraps(func)
        async def search_runs(*args, **kwargs):
            print("args"+args[0])
            print(self.executors[0])
            mlflow.set_tracking_uri(client.get_tracker_uri(True))
            print("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
            runs = mlflow.search_runs(experiment_ids=["2"],
                filter_string=self.filter_string,
                order_by=self.order_by, output_format='list')
            print(runs[0].to_dictionary())
            #run_ids = runs[0].info.run_id
            print(func.__name__)
            return await func(["1111111","222222","333333"])
        return search_runs