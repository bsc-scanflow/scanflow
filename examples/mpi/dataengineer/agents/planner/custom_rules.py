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

def no_strategy(node: Node):
    body = node.body
    
    if not node.oversubscribe:
        nWorkers = 1
        for i, task in enumerate(body['spec']['tasks']):
            if task['name'] == node.workerName:
                body['spec']['tasks'][i]['replicas'] = node.nNodes
                nWorkers = node.nNodes
                    
        #mpi settings
        mpiplugins = [f"--oversubscribe={node.oversubscribe}",
                      f"--masterName={node.masterName}",
                      f"--workerName={node.workerName}",
                      f"--nTasks={node.nTasks}",
                      f"--nWorkers={nWorkers}",
                      f"--nCpusPerTask={node.nCpusPerTask}",
                      f"--memoryPerTask={node.memoryPerTask}"]
        body['spec']['plugins']['mpi'] = mpiplugins
   
    logging.info(f"new body: {body}")
    node.body = body
    

def enable_granularity_strategy(node: Node):
    body = node.body
    logging.info(f"old body: {body}") 
    
    ##granularity-aware
    if not node.oversubscribe:
        nWorkers = 1
        for i, task in enumerate(body['spec']['tasks']):
            if task['name'] == node.workerName:
                if node.characteristic == "network":
                    body['spec']['tasks'][i]['replicas'] = node.nNodes
                    nWorkers = node.nNodes
                elif node.characteristic == "cpu":
                    body['spec']['tasks'][i]['replicas'] = node.nTasks
                    nWorkers = node.nTasks
                elif node.characteristic == "memory":
                    body['spec']['tasks'][i]['replicas'] = node.nTasks
                    nWorkers = node.nTasks
                else:
                    logging.info(f"unknown node characteristic")
                    body['spec']['tasks'][i]['replicas'] = node.nNodes
                    nWorkers = node.nNodes
                    
        #mpi settings
        mpiplugins = [f"--oversubscribe={node.oversubscribe}",
                      f"--masterName={node.masterName}",
                      f"--workerName={node.workerName}",
                      f"--nTasks={node.nTasks}",
                      f"--nWorkers={nWorkers}",
                      f"--nCpusPerTask={node.nCpusPerTask}",
                      f"--memoryPerTask={node.memoryPerTask}"]
        body['spec']['plugins']['mpi'] = mpiplugins
            
        body['metadata']['annotations'] = {
            "volcano.sh/task-groups" : f"{node.workerName}:{node.nNodes}"
        }
   
    logging.info(f"new body: {body}")
    node.body = body
    
    return node