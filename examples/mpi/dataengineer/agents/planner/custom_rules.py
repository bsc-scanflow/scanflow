from typing import List

import logging

from scanflow.server.schemas.app import Node
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


def select_strategy(plugins: List[str]):
    #this can be used to deal with the strategies' conflicts
    #now we only have one "granularity"
    return plugins[0]

def enable_granularity_strategy(node: Node):
    body = node.body
    logging.info(f"old body: {body}") 
    
    ##granularity-aware
    if not node.oversubscribe:
        for i, task in enumerate(body['spec']['tasks']):
            if task['name'] == node.workerName:
                if node.characteristic == "network":
                    body['spec']['tasks'][i]['replicas'] = node.nNodes
                elif node.characteristic == "cpu":
                    body['spec']['tasks'][i]['replicas'] = node.nTasks
                elif node.characteristic == "memory":
                    body['spec']['tasks'][i]['replicas'] = node.nTasks
                else:
                    logging.info(f"unknown node characteristic")
                    body['spec']['tasks'][i]['replicas'] = node.nNodes
            
    ##resources limits/requests
    
    #"resources": {"requests": {"cpu": 8, "memory": "40Gi"}, "limits": {"cpu": 8, "memory": "40Gi"}}
    
   
    logging.info(f"new body: {body}")
    node.body = body
    
    return node