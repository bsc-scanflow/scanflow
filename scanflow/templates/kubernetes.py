import re
from kubernetes import client, config, utils
from os import path
from typing import List, Dict
import yaml
import pyaml
import json
from scanflow.tools.seldon_dict import remove_empty_elements, verify_dict
#from pick import pick  # install pick using `pip install pick`

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)



class Kubernetes:
    def __init__(self,
                 k8s_config_file=None):

        try:
            logging.info(f"loading kubernetes configuration from {k8s_config_file}")
            config.load_kube_config(config_file=k8s_config_file)
            logging.info(f"found local kubernetes configuration")
        except Exception:
            logging.info(f"cannot find local kubernetes configuration {k8s_config_file}, trying incluster config")
            config.load_incluster_config()
            logging.info("set incluster kubernetes config")


    def create_namespace(self, namespace):
        namespacebody = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace)
        )
        api_instance = client.CoreV1Api()
        try:
            back = api_instance.create_namespace(namespacebody)
            logging.info(f"create_namespace true")
            return True
        except: 
            logging.error(f"create_namespace error") 
            return False
            

    def delete_namespace(self, name):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespace(name=name)
            logging.info(f"delete_namespace true")
            return True
        except: 
            logging.error(f"delete_namespace error")
            return False 

# Service
#{'api_version': 'v1',
# 'kind': 'Service',
# 'metadata': {'annotations': None,
#              'cluster_name': None,
#              'creation_timestamp': None,
#              'deletion_grace_period_seconds': None,
#              'deletion_timestamp': None,
#              'finalizers': None,
#              'generate_name': None,
#              'generation': None,
#              'labels': None,
#              'managed_fields': None,
#              'name': 'my-service',
#              'namespace': None,
#              'owner_references': None,
#              'resource_version': None,
#              'self_link': None,
#              'uid': None},
# 'spec': {'cluster_ip': None,
#          'external_i_ps': None,
#          'external_name': None,
#          'external_traffic_policy': None,
#          'health_check_node_port': None,
#          'ip_family': None,
#          'load_balancer_ip': None,
#          'load_balancer_source_ranges': None,
#          'ports': [{'name': None,
#                     'node_port': None,
#                     'port': 80,
#                     'protocol': 'TCP',
#                     'target_port': 9376}],
#          'publish_not_ready_addresses': None,
#          'selector': {'scanflow': 'MyApp'},
#          'session_affinity': None,
#          'session_affinity_config': None,
#          'type': None},
# 'status': None}
#
    def build_servicePort(self, protocol=None, port=None, targetPort=None, nodePort=None):
        ports=[]
        ports.append(
            client.V1ServicePort(
                protocol=protocol,
                port=port,
                target_port=targetPort,
                node_port=nodePort
            )
        )
        return ports

    def build_service(self, namespace, name, label=None, ports=None, type=None):
        service = client.V1Service()
        service.api_version = "v1"
        service.kind = "Service"
        service.metadata = client.V1ObjectMeta(
            name=name,
            namespace=namespace
        )
        spec = client.V1ServiceSpec(
            selector = {label: name},
            ports = ports,
            type = type
        )
        service.spec = spec
        return service

    def create_service(self, namespace, body):
        api_instance = client.CoreV1Api()
        try:
            api_instance.create_namespaced_service(namespace=namespace, body=body)
            logging.info(f"create_service true")
            return True
        except:
            logging.error(f"create_service error") 
            return False

    def delete_service(self, namespace, name):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespaced_service(name=name, namespace=namespace)
            logging.info(f"delete_service true")
            return True
        except:
            logging.error(f"delete_service error") 
            return False

# Secret
#{'api_version': None,
# 'data': {'password': 'bXlwYXNzd29yZA==', 'username': 'bXl1c2VybmFtZQ=='},
# 'kind': None,
# 'metadata': {'annotations': None,
#              'cluster_name': None,
#              'creation_timestamp': None,
#              'deletion_grace_period_seconds': None,
#              'deletion_timestamp': None,
#              'finalizers': None,
#              'generate_name': None,
#              'generation': None,
#              'labels': None,
#              'managed_fields': None,
#              'name': 'mysecret',
#              'namespace': None,
#              'owner_references': None,
#              'resource_version': None,
#              'self_link': None,
#              'uid': None},
# 'string_data': None,
# 'type': 'Opaque'}

    def build_secret(self, name, namespace, stringData):
        secret = client.V1Secret()
        secret.metadata = client.V1ObjectMeta(name=name,
        namespace=namespace)
        secret.type = "Opaque"
        secret.string_data = stringData
        return secret

    def create_secret(self, namespace, body):
        api_instance = client.CoreV1Api()
        #try:
        back = api_instance.create_namespaced_secret(namespace=namespace, body=body)
        logging.info(f"create_secret true")
        return True
        #except:
        #    logging.error(f"create_secret error")
        #    return False

    def delete_secret(self, namespace, name):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespaced_secret(name=name, namespace=namespace)
            logging.info(f"delete_secret true")
            return True
        except:
            logging.error(f"delete_secret error")
            return False

    def build_configmap(self, name, namespace, data):
        configmap = client.V1ConfigMap()
        configmap.metadata = client.V1ObjectMeta(
            name = name,
            namespace = namespace
        )
        configmap.data = data
        return configmap

    def create_configmap(self, namespace, body):
        api_instance = client.CoreV1Api()
        try: 
            back = api_instance.create_namespaced_config_map(namespace=namespace,body=body)
            logging.info(f"create_configmap true")
            return True
        except:
            logging.error(f"create_configmap error")
            return False

    def delete_configmap(self, namespace, name):
        api_instance = client.CoreV1Api()
        try: 
            api_instance.delete_namespaced_config_map(namespace=namespace, name=name)
            logging.info(f"delete_configmap true")
            return True
        except:
            logging.error(f"delete_configmap error")
            return False



# Deployment
#{'api_version': None,
# 'kind': None,
# 'metadata': {'annotations': None,
#              'cluster_name': None,
#              'creation_timestamp': None,
#              'deletion_grace_period_seconds': None,
#              'deletion_timestamp': None,
#              'finalizers': None,
#              'generate_name': None,
#              'generation': None,
#              'labels': None,
#              'managed_fields': None,
#              'name': 'my-busybox',
#              'namespace': None,
#              'owner_references': None,
#              'resource_version': None,
#              'self_link': None,
#              'uid': None},
# 'spec': {'min_ready_seconds': None,
#          'paused': None,
#          'progress_deadline_seconds': None,
#          'replicas': None,
#          'revision_history_limit': None,
#          'selector': {'match_expressions': None,
#                       'match_labels': {'app': 'busybox'}},
#          'strategy': None,
#          'template': {'metadata': {'annotations': None,
#                                    'cluster_name': None,
#                                    'creation_timestamp': None,
#                                    'deletion_grace_period_seconds': None,
#                                    'deletion_timestamp': None,
#                                    'finalizers': None,
#                                    'generate_name': None,
#                                    'generation': None,
#                                    'labels': {'app': 'busybox'},
#                                    'managed_fields': None,
#                                    'name': 'busybox',
#                                    'namespace': None,
#                                    'owner_references': None,
#                                    'resource_version': None,
#                                    'self_link': None,
#                                    'uid': None},
#                       'spec': {'active_deadline_seconds': None,
#                                'affinity': None,
#                                'automount_service_account_token': None,
#                                'containers': [{'args': ['sleep', '3600'],
#                                                'command': None,
#                                                'env': None,
#                                                'env_from': None,
#                                                'image': 'busybox:1.26.1',
#                                                'image_pull_policy': None,
#                                                'lifecycle': None,
#                                                'liveness_probe': None,
#                                                'name': 'my-busybox',
#                                                'ports': None,
#                                                'readiness_probe': None,
#                                                'resources': None,
#                                                'security_context': None,
#                                                'startup_probe': None,
#                                                'stdin': None,
#                                                'stdin_once': None,
#                                                'termination_message_path': None,
#                                                'termination_message_policy': None,
#                                                'tty': None,
#                                                'volume_devices': None,
#                                                'volume_mounts': None,
#                                                'working_dir': None}],
#                                'dns_config': None,
#                                'dns_policy': None,
#                                'enable_service_links': None,
#                                'ephemeral_containers': None,
#                                'host_aliases': None,
#                                'host_ipc': None,
#                                'host_network': None,
#                                'host_pid': None,
#                                'hostname': None,
#                                'image_pull_secrets': None,
#                                'init_containers': None,
#                                'node_name': None,
#                                'node_selector': None,
#                                'overhead': None,
#                                'preemption_policy': None,
#                                'priority': None,
#                                'priority_class_name': None,
#                                'readiness_gates': None,
#                                'restart_policy': None,
#                                'runtime_class_name': None,
#                                'scheduler_name': None,
#                                'security_context': None,
#                                'service_account': None,
#                                'service_account_name': None,
#                                'share_process_namespace': None,
#                                'subdomain': None,
#                                'termination_grace_period_seconds': None,
#                                'tolerations': None,
#                                'topology_spread_constraints': None,
#                                'volumes': None}}},
# 'status': None}



    def build_deployment(self, namespace=None, name=None, label=None, image=None, volumes=None, env=None, env_from=None, volumeMounts=None): 
        spec = client.V1DeploymentSpec(
            selector=client.V1LabelSelector(match_labels={label:name}),
            template=client.V1PodTemplateSpec(),
            replicas=1,
        )
        container = client.V1Container(
            name=name,
            image=image,
            image_pull_policy="Always",
            env=env,
            env_from=env_from,
            volume_mounts=volumeMounts
        )
        spec.template.metadata = client.V1ObjectMeta(
            name=name,
            labels={label:name},
        )
        spec.template.spec = client.V1PodSpec(
            containers = [container],
            volumes= volumes
        )

        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=name,
                namespace=namespace
            ),
            spec=spec,
        )
        return deployment

    def create_deployment(self, namespace, body):
        api_instance = client.AppsV1Api()
        try:
            back = api_instance.create_namespaced_deployment(namespace=namespace, body=body)
            logging.info(f"create_deployment true ")
            return True
        except:
            logging.error(f"create_deployment error ") 
            return False

    def apply_deployment(self, namespace, name, deployment):
        api_instance = client.AppsV1Api()
        back = api_instance.replace_namespaced_deployment(name=name, namespace=namespace, body=deployment)
        return back
    
    def delete_deployment(self, namespace, name):
        api_instance = client.AppsV1Api()
        try:
            api_instance.delete_namespaced_deployment(name=name, namespace=namespace, body=client.V1DeleteOptions(propagation_policy="Foreground", grace_period_seconds=5))
            logging.info(f"delete_deployment true")
            return True
        except:
            logging.error(f"delete_deployment error") 
            return False

# PVC
#{'api_version': 'v1',
# 'kind': 'PersistentVolumeClaim',
# 'metadata': {'annotations': None,
#              'cluster_name': None,
#              'creation_timestamp': None,
#              'deletion_grace_period_seconds': None,
#              'deletion_timestamp': None,
#              'finalizers': None,
#              'generate_name': None,
#              'generation': None,
#              'labels': None,
#              'managed_fields': None,
#              'name': 'my-pvc',
#              'namespace': None,
#              'owner_references': None,
#              'resource_version': None,
#              'self_link': None,
#              'uid': None},
# 'spec': {'access_modes': ['ReadWriteMany'],
#          'data_source': None,
#          'resources': {'limits': None, 'requests': {'storage': '16Mi'}},
#          'selector': None,
#          'storage_class_name': None,
#          'volume_mode': None,
#          'volume_name': None},
# 'status': None}

    def build_persistentvolumeclaim(self, namespace=None, name=None, storage_class_name=None, access_mode=None, storage=None):
        return client.V1PersistentVolumeClaim(
            api_version='v1',
            kind='PersistentVolumeClaim',
            metadata=client.V1ObjectMeta(
                namespace=namespace,
                name=name
            ),
            spec=client.V1PersistentVolumeClaimSpec(
                storage_class_name=storage_class_name,
                access_modes=[
                    access_mode
                ],
                resources=client.V1ResourceRequirements(
                    requests={
                        'storage': storage
                    }
                )
            )
    )

    def create_persistentvolumeclaim(self, namespace, body):
        api_instance = client.CoreV1Api()
        try:
            api_instance.create_namespaced_persistent_volume_claim(namespace=namespace, body=body)
            logging.info(f"create_pvc true")
            return True
        except:
            logging.error(f"create_pvc error") 
            return False

    def delete_persistentvolumeclaim(self, namespace, name):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespaced_persistent_volume_claim(namespace=namespace, name=name)
            logging.info(f"delete_pvc true")
            return True
        except:
            logging.error(f"delete_pvc error") 
            return False


#PV
#{'api_version': 'v1',
# 'kind': 'PersistentVolume',
# 'metadata': {'annotations': None,
#              'cluster_name': None,
#              'creation_timestamp': datetime.datetime(2021, 4, 5, 18, 22, 1, tzinfo=tzutc()),
#              'deletion_grace_period_seconds': None,
#              'deletion_timestamp': None,
#              'finalizers': ['kubernetes.io/pv-protection'],
#              'generate_name': None,
#              'generation': None,
#              'labels': None,
#              'managed_fields': [{'api_version': 'v1',
#                                  'fields_type': 'FieldsV1',
#                                  'fields_v1': {'f:spec': {'f:accessModes': {},
#                                                           'f:capacity': {'.': {},
#                                                                          'f:storage': {}},
#                                                           'f:hostPath': {'.': {},
#                                                                          'f:path': {},
#                                                                          'f:type': {}},
#                                                           'f:persistentVolumeReclaimPolicy': {},
#                                                           'f:storageClassName': {},
#                                                           'f:volumeMode': {}},
#                                                'f:status': {'f:phase': {}}},
#                                  'manager': 'OpenAPI-Generator',
#                                  'operation': 'Update',
#                                  'time': datetime.datetime(2021, 4, 5, 18, 22, 1, tzinfo=tzutc())}],
#              'name': 'my-pv',
#              'namespace': None,
#              'owner_references': None,
#              'resource_version': '18289917',
#              'self_link': '/api/v1/persistentvolumes/my-pv',
#              'uid': 'f10dfc26-7c0d-43bc-aa95-135708c5d6b9'},
# 'spec': {'access_modes': ['ReadWriteMany'],
#          'aws_elastic_block_store': None,
#          'azure_disk': None,
#          'azure_file': None,
#          'capacity': {'storage': '1Gi'},
#          'cephfs': None,
#          'cinder': None,
#          'claim_ref': None,
#          'csi': None,
#          'fc': None,
#          'flex_volume': None,
#          'flocker': None,
#          'gce_persistent_disk': None,
#          'glusterfs': None,
#          'host_path': {'path': '/gpfs/bsc_home/xpliu/scanflow', 'type': ''},
#          'iscsi': None,
#          'local': None,
#          'mount_options': None,
#          'nfs': None,
#          'node_affinity': None,
#          'persistent_volume_reclaim_policy': 'Retain',
#          'photon_persistent_disk': None,
#          'portworx_volume': None,
#          'quobyte': None,
#          'rbd': None,
#          'scale_io': None,
#          'storage_class_name': 'local-path',
#          'storageos': None,
#          'volume_mode': 'Filesystem',
#          'vsphere_volume': None},
# 'status': {'message': None, 'phase': 'Pending', 'reason': None}}
#

    def build_persistentvolume(self, name=None, storage=None, hostpath=None):
        return client.V1PersistentVolume(
            api_version='v1',
            kind='PersistentVolume',
            metadata=client.V1ObjectMeta(
                name=name
            ),
            spec=client.V1PersistentVolumeSpec(
                #storage_class_name='local-path',
                access_modes=[
                    'ReadWriteMany'
                ],
                capacity={'storage': storage},
                host_path={'path': hostpath }
            )
        )

    def create_persistentvolume(self, body):
        api_instance = client.CoreV1Api()
        try:
            api_instance.create_persistent_volume(body=body)
            logging.info(f"create_pv true")
            return True
        except:
            logging.error(f"create_pv error")
            return False

    def delete_persistentvolume(self, name):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_persistent_volume(name=name)
            logging.info(f"delete_pv true")
            return True
        except:
            logging.error(f"delete_pv error")
            return False



#Rolebinding

    def build_rolebinding(self, namespace):
        return client.V1RoleBinding(
            api_version='rbac.authorization.k8s.io/v1',
            kind='RoleBinding',
            metadata=client.V1ObjectMeta(
                name='default-admin',
                namespace=namespace
            ), 
            role_ref=client.V1RoleRef(
                kind='ClusterRole',
                name='cluster-admin',
                api_group=""
            ),
            subjects=[client.V1Subject(
                namespace=namespace,
                name='default',
                kind='ServiceAccount',
                api_group=""
            )]
        )

    def create_rolebinding(self, namespace, body):
        api_instance = client.RbacAuthorizationV1Api()
        try:
            api_instance.create_namespaced_role_binding(namespace, body)
            logging.info(f"create_rolebinding info")
            return True
        except:
            logging.error(f"create_rolebinding error")
            return False

    def delete_rolebinding(self, namespace, name='default-admin'):
        api_instance = client.RbacAuthorizationV1Api()
        try:
            api_instance.delete_namespaced_role_binding(name=name, namespace=namespace)
            logging.info(f"delete_rolebinding info")
            return True
        except:
            logging.error(f"delete_rolebinding error")
            return False



    #SeldonDeployment
    def create_seldonDeployment(self, namespace, body):
        api_client = client.CustomObjectsApi()
        yaml_str = pyaml.dump(body)
        body = yaml.safe_load(yaml_str)
        body = verify_dict(remove_empty_elements(body))
        #logging.info(f"seldon deployment {yaml_str} {body}")
        logging.info("Submitting workflow to Seldon")
        try:
            response = api_client.create_namespaced_custom_object(
                "machinelearning.seldon.io",
                "v1",
                namespace,
                "seldondeployments",
                body,
                #pretty='pretty_example'
            )
            logging.info(
                'Workflow %s has been submitted in "%s" namespace!'
                % (response.get("metadata", {}).get("name"), namespace)
            )
            return response
        except Exception as e:
            logging.error("Failed to submit workflow to seldon")
            raise e


    def delete_seldonDeployment(self, namespace, name):
    
        api_client = client.CustomObjectsApi()
        try:
            return api_client.delete_namespaced_custom_object(
                "machinelearning.seldon.io",
                "v1",
                namespace,
                "seldondeployments",
                name,
                body=client.V1DeleteOptions(propagation_policy="Foreground", grace_period_seconds=5),
            )
        except client.api_client.rest.ApiException as e:
            raise Exception("Exception when deleting the workflow: %s\n" % e)
        
    def get_virtualservice(self, namespace, name):
        
        api_client = client.CustomObjectsApi()
        try:
            api_response = api_client.get_namespaced_custom_object(
                "networking.istio.io",
                "v1alpha3",
                namespace,
                "virtualservices",
                name)
            logging.info(f"get vs:{api_response}")
            return api_response
        except client.api_client.rest.ApiException as e:
            raise Exception("Exception when calling CustomObjectsApi->get_namespaced_custom_object: %s\n" % e)
        
    def replace_virtualservice(self, namespace, name, body):
        
        api_client = client.CustomObjectsApi()
        try:
            response =  api_client.replace_namespaced_custom_object(
                "networking.istio.io",
                "v1alpha3",
                namespace,
                "virtualservices",
                name,
                body
            )
            logging.info(
                'virtualservice %s has been replaced in "%s" namespace!'
                % (response.get("metadata", {}).get("name"), namespace)
            )
            return response
        except client.api_client.rest.ApiException as e:
            raise Exception("Failed to patch virtualservice")


###pod spec: affinity, nodeselector, priority, schedulerName, volume
    def build_podSpec(self, 
                      containers: List[client.V1Container],
                      affinity: client.V1Affinity = None,
                      node_name: str = None,
                      node_selector: dict = None,
                      preemption_policy: str = None,
                      priority: int = None,
                      priority_class_name: str = None,
                      restart_policy: str = None,
                      scheduler_name: str = None,
                      volumes: List[client.V1Volume] = None,
                      active_deadline_seconds: int = None): 
        spec = client.V1PodSpec(containers=containers,
        affinity=affinity, node_name=node_name, node_selector=node_selector, preemption_policy=preemption_policy, priority=priority, priority_class_name=priority_class_name, restart_policy=restart_policy, scheduler_name=scheduler_name, volumes=volumes, active_deadline_seconds=active_deadline_seconds)
        return spec  

    def build_container(self,
                        name: str,
                        image: str,
                        args: List[str] = None,
                        command: List[str] = None,
                        env: List[client.V1EnvVar] = None,
                        env_from: List[client.V1EnvFromSource] = None,
                        image_pull_policy: str = "Always",
                        resources: client.V1ResourceRequirements = None,
                        volume_mounts: List[client.V1VolumeMount] = None,
                        working_dir: str = None):
        container = client.V1Container(
            name=name,
            image=image,
            args=args,
            command=command,
            env=env,
            env_from=env_from,
            image_pull_policy=image_pull_policy,
            resources=resources,
            volume_mounts=volume_mounts,
            working_dir=working_dir
        )
        
        return container

    def build_env(self, **kwargs):
        env_list = []
        for k, v in kwargs.items():
            env_list.append(
                client.V1EnvVar(
                    name=k,
                    value=v
                ),
            )
        return env_list

    def build_env_from_source(self, **kwargs):
        env_from_list = []
        for k, v in kwargs.items():
            if k == "config_map_ref":
                env_from_list.append(
                    client.V1EnvFromSource(
                        config_map_ref=client.V1ConfigMapEnvSource(
                            name = v
                        )
                    )
                )
            elif k == "secret_ref":
                env_from_list.append(
                    client.V1EnvFromSource(
                        secret_ref=client.V1SecretEnvSource(
                            name = v
                        )
                    )
                )
        return env_from_list

    def build_volumeMounts(self, **kwargs):
        volumeMounts = []
        for k, v in kwargs.items():
            volumeMounts.append(
                client.V1VolumeMount(
                    name=k,
                    mount_path=v
                ),
            )
        return volumeMounts

    def build_volumes(self, **kwargs):
        volumes = []
        for k, v in kwargs.items():
            volumes.append(
                client.V1Volume(
                    name=k,
                    persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=v)
                ),
            )
        return volumes