from scanflow.client import ScanflowClient

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

# scanflow client
client = ScanflowClient(
              #if you defined "SCANFLOW_SERVER_URI", you dont need to provide this
              #scanflow_server_uri="http://172.30.0.50:46666",
              verbose=True)

def find_antiaffinity_config():
    antipodaffinity = {}
    
    # #resource requirment
    # resources = client.V1ResourceRequirements(requests={'cpu': '16', 'memory': '50Gi'},
    #                                           limits={'cpu': '16', 'memory': '50Gi'})
    
    #affinity
    # https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity
    #seldon-app: online-inference-single-online-inference-single
    label_selector_batch = client.V1LabelSelector(
                             match_expressions=[
                                 client.V1LabelSelectorRequirement(
                                     key = 'seldon-app',
                                     operator = 'In',
                                     values = ['online-inference-single-online-inference-single']
                                 )
                             ]
                  )
    
    
    podanti_selector_batch = client.V1PodAffinityTerm(topology_key='kubernetes.io/hostname',
                                                      label_selector=[label_selector_batch])
        
    podanti_affinity_batch = client.V1PodAntiAffinity(
            required_during_scheduling_ignored_during_execution=podanti_selector_batch)
    
    affinity = client.V1Affinity(pod_anti_affinity=podanti_affinity_batch)

    antipodaffinity = affinity.to_dict()
   
    logging.info(f"antipodaffinity dict: {antipodaffinity}") 
    return antipodaffinity

def find_scaling_config():
    
    #keda scaler
    trigger_request_rate = client.ScalerTriggerPrometheus(
        serverAddress = 'http://prometheus.istio-system:9090',
        metricName = 'istio_requests_total',
        query = 'sum(rate(istio_requests_total{connection_security_policy="mutual_tls",destination_service=~"online-inference-single-online-inference-single.scanflow-mlperf-dataengineer.svc.cluster.local",reporter=~"destination",source_workload=~"istio-ingressgateway",source_workload_namespace=~"istio-system"}[5m]))',
        threshold = '\'20\'',
    )

    kedaSpec = client.KedaSpec(maxReplicaCount=10,
                           minReplicaCount=3,
                           pollingInterval=10,
                           cooldownPeriod=10,
                           triggers=[trigger_request_rate])
    
    logging.info(f"kedascaling dict: {kedaSpec.to_dict()}")
    return kedaSpec.to_dict()

def find_backup_service():
    backupservice = {'modelUri','s3://scanflow/scanflow-mlperf-dataengineer/1/fde8c5e912a84b8385e1154053c3e759/artifacts/mlperf-resnet/model'}
    
    logging.info(f"backupservice dict: {backupservice}")
    return backupservice

def check_availability(avireplicas, name):
    if avireplicas == 0:
        patch = {"route": [
					{
						"destination": {
							"host": f"{name}-{name}",
							"port": {
								"number": 5001
							},
							"subset": f"{name}"
						},
						"weight": 0
					},
					{
						"destination": {
							"host": f"{name}-backup",
							"port": {
								"number": 5001
							},
							"subset": "backup"
						},
						"weight": 100
					}
				]}
        return patch
    else:
        return None
    