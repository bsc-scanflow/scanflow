import requests
from functools import wraps
from scanflow.agent.config.httpClient import http_client
from scanflow.agent.schemas.message import ActuatorMessage
from scanflow.agent.schemas.request import Request
from scanflow.tools.env import get_env
import json

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)

class actuator:
    def __init__(self,
                 path:str,
                 depender:str,
                 namespace: str = get_env("NAMESPACE")):
        self.path = path
        self.depender = depender
        self.namespace = namespace

    def __call__(self, func):
        @wraps(func)
        async def make_call(run_ids, *args, **kwargs):
            logging.info(f"run_ids: {run_ids}")
            print(type(args))
            print(type(kwargs))
            print(args)
            print(kwargs)

            func(run_ids, args, kwargs)

            #print(type(*args))

            #url = f"http://{self.depender}.{self.default}.svc.cluster.local"
            url = f"http://172.30.0.49:4005{self.path}"
            logging.info(f"sending request to {url}") 
            request = Request(run_ids = run_ids,
                              args = args,
                              kwargs = kwargs)
            #print(json.dumps(request.dict()))
            async with http_client.session.post(url, data=json.dumps(request.dict())) as response:
                status = response.status
                text = await response.json()
 
            await self.save_message(
                ActuatorMessage(type="actuator",
                                function=f"{func.__name__}",
                                depender=self.depender,
                                url=url,
                                status=status,
                                detail=text['detail'])
            )

        return make_call

    async def save_message(self, actuatorMessage: ActuatorMessage):
        agent_name = get_env("AGENT_NAME")
        mlflow.set_experiment(f"{agent_name}-agent")
        with mlflow.start_run(run_name=f"{actuatorMessage.type} - {actuatorMessage.function}"):
            mlflow.log_dict(actuatorMessage.dict(), "log.json")