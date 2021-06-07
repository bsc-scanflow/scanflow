from typing import List, Tuple
from scanflow.agent.schemas.requestData import RequestData
from starlette.requests import Request
from scanflow.tools.env import get_env
from scanflow.agent.schemas.message import SensorMessage

import mlflow
from scanflow.client import ScanflowTrackerClient
client = ScanflowTrackerClient(verbose=True)


class SensorDependency:
    def __init__(self):
        pass

    async def __call__(self, request: Request, data: RequestData):
        print(request.__dict__)
        print(request.url.path)
        print(request.get('endpoint').__name__)
        print(data.args)
        print(data.kwargs)
        mlflow.set_tracking_uri(client.get_tracker_uri(True))
        print("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        if "islocal" in data.kwargs:
            if data.kwargs["islocal"] is False:
                mlflow.set_tracking_uri(client.get_tracker_uri(False))
                print("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        if "run_ids" in data.kwargs:
            runs = list(map(mlflow.get_run, data.kwargs['run_ids']))
            data.kwargs['runs'] = runs
            active_run = self.save_message(function=request.get('endpoint').__name__ , nodes=data.kwargs['run_ids'], client=request.get('client'), server=request.get('server')+(request.url.path,))
        else:
            active_run = self.save_message(function=request.get('endpoint').__name__ , nodes=None, client=request.get('client'), server=request.get('server')+(request.url.path,))

        return (active_run, data.args, data.kwargs)

    def save_message(self, function:str, nodes:List[str], client: tuple, server: tuple):
        sensorMessage = SensorMessage(type="sensor",
                                  function=function,
                                  nodes=nodes,
                                  client=client,
                                  server=server)
        agent_name = get_env("AGENT_NAME")
        mlflow.set_experiment(f"{agent_name}-agent")
        with mlflow.start_run(run_name=f"{sensorMessage.type} - {sensorMessage.function}"):
            mlflow.log_dict(sensorMessage.dict(), "log.json")
            return mlflow.active_run()

sensor_dependency = SensorDependency()