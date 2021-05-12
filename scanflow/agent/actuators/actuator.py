import requests
from functools import wraps
from scanflow.agent.config.httpClient import http_client

class actuator:
    def __init__(self,
                 path:str,
                 depender:str):
        self.path = path
        self.depender = depender

    def __call__(self, func):
        @wraps(func)
        async def make_call(run_ids, *args, **kwargs):
            print(run_ids)
            i = 0
            for x in args:
                print(f"{i}"+x)
                i = i+1
            print(f"{self.path} -- {self.depender}")
            url = f"http://172.30.0.49:4004/{self.path}" 
            async with http_client.session.get(url) as response:
                result = await response.json()

            print(result['Hello'])
            #response = requests.get(url=url, 
            #headers={"accept": "application/json"})
            #print(f"{self.path} -- {response.status} -- {response.json()} -- {response.text}")
            #func(response.text)
            print(func.__name__)
        return make_call