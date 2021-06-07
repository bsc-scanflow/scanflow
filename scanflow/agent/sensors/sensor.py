from typing import List, Optional
from functools import wraps
from scanflow.tools.env import get_env
from scanflow.agent.schemas.message import SensorMessage

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)

class sensor:
    def __init__(self,
                 nodes: List[str] = None,
                 filter_string: str = '', 
                 order_by: Optional[List[str]] = None,
                 max_results: int = 100,
                 islocal: Optional[bool] = True):
        self.islocal = islocal
        self.nodes = nodes
        # default search all runs
        self.filter_string = filter_string
        self.order_by = order_by
        self.max_results = max_results

    def __call__(self, func):
        @wraps(func)
        async def search_runs(*args, **kwargs):
            print(args)
            print(type(args))
            print(kwargs)
            print(type(kwargs))
            if self.nodes is not None:
                mlflow.set_tracking_uri(client.get_tracker_uri(self.islocal))
                logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

                experiment_ids = self.get_experiment_ids()
                logging.info(f"sensor get runs from experiment_ids: {experiment_ids}")
                
                runs = mlflow.search_runs(experiment_ids=experiment_ids,
                    filter_string=self.filter_string,
                    max_results=self.max_results,
                    order_by=self.order_by, output_format='list')

                metric_value = await func(runs, args, kwargs)

                await self.save_message(
                    SensorMessage(type="sensor",
                                  function=f"{func.__name__}",
                                  nodes=self.nodes,
                                  value=metric_value)
                )
        return search_runs

    def get_experiment_ids(self):
        experiments =  list(map(mlflow.get_experiment_by_name, self.nodes))
        experiment_ids = list(map(lambda experiment: experiment.experiment_id, experiments))
        return experiment_ids

    async def save_message(self, sensorMessage: SensorMessage):
        #mlflow.set_tracking_uri(client.get_tracker_uri(self.islocal))
        #logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        agent_name = get_env("AGENT_NAME")
        mlflow.set_experiment(f"{agent_name}-agent")
        with mlflow.start_run(run_name=f"{sensorMessage.type} - {sensorMessage.function}"):
            mlflow.log_dict(sensorMessage.dict(), "log.json")
            
    
    