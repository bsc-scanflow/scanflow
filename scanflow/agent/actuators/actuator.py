import requests
from functools import wraps
from scanflow.agent.config.httpClient import http_client
from scanflow.agent.schemas.message import ActuatorMessage
from scanflow.agent.schemas.requestData import RequestData
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
        async def make_call(*args, **kwargs):
            print(type(args))
            print(type(kwargs))
            print(args)
            print(kwargs)

            args, kwargs = func(args=args, kwargs=kwargs)

            #url = f"http://{self.depender}.{self.namespace}.svc.cluster.local{self.path}"
            url = f"http://172.30.0.49:4005{self.path}"
            logging.info(f"sending request to {url}") 
            requestData = RequestData(
                              args = args,
                              kwargs = kwargs)
            #print(json.dumps(request.dict()))
            async with http_client.session.post(url, data=json.dumps(requestData.dict())) as response:
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