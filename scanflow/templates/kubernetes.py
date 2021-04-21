from kubernetes import client, config, utils
from os import path
import yaml
from pick import pick  # install pick using `pip install pick`

import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


class Kubernetes:
    def __init__(self,
                 configdir=None,
                 verbose=True):
        self.verbose = verbose
        
        if configdir is not None:
            config.load_kube_config(configdir)
        else:
            config.load_kube_config()

        config.load_incluster_config()


    def create_namespace(self, namespace):
        namespacebody = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace)
        )
        api_instance = client.CoreV1Api()
        try:
            api_instance.create_namespace(namespacebody)
        except: 
            logging.error(f"create_namespace error") 
            

    def delete_namespace(self, namespace):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespace(name=namespace)
        except: 
            logging.error(f"delete_namespace error") 

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

    def build_service(self, namespace=None, name=None, label=None, ports=None, type=None):
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

    def create_service(self, namespace=None, service=None):
        api_instance = client.CoreV1Api()
        try:
            api_instance.create_namespaced_service(namespace=namespace, body=service)
        except:
            logging.error(f"create_service error") 

    def delete_service(self, namespace=None, name=None):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespaced_service(name=name, namespace=namespace)
        except:
            logging.error(f"delete_service error") 

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

    def build_secret(self):
        secret = client.V1Secret()
        secret.metadata = client.V1ObjectMeta(name="mysecret")
        secret.type = "Opaque"
        secret.data = {"username": "bXl1c2VybmFtZQ==", "password": "bXlwYXNzd29yZA=="}
        return secret

    def create_secret(self, secret=None, namespace='default'):
        api_instance = client.CoreV1Api()
        back = api_instance.create_namespaced_secret(namespace="default", body=secret)
        return back

    def delete_secret(self):
        api_instance = client.CoreV1Api()
        back = api_instance.delete_namespaced_secret(name="mysecret", namespace="default")
        return back


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

    def build_env(self, **kwargs):
        envs = []
        for k, v in kwargs.items():
            envs.append(
                client.V1EnvVar(
                    name=k,
                    value=v
                ),
            )
        return envs

    def build_volumeMount(self, **kwargs):
        volumeMount = []
        for k, v in kwargs.items():
            volumeMount.append(
                client.V1VolumeMount(
                    name=k,
                    mount_path=v
                ),
            )
        return volumeMount

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

    def build_deployment(self, namespace=None, name=None, label=None, image=None, volumes=None, env=None, volumeMount=None): 
        spec = client.V1DeploymentSpec(
            selector=client.V1LabelSelector(match_labels={label:name}),
            template=client.V1PodTemplateSpec(),
            replicas=1,
        )
        container = client.V1Container(
            name=name,
            image=image,
            image_pull_policy="IfNotPresent",
            env=env,
            volume_mounts=volumeMount
        )
        spec.template.metadata = client.V1ObjectMeta(
            name=name,
            labels={"scanflow":name},
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

    def create_deployment(self, namespace=None, deployment=None):
        api_instance = client.AppsV1Api()
        try:
            api_instance.create_namespaced_deployment(namespace=namespace, body=deployment)
        except:
            logging.error(f"create_deployment error") 

    def apply_deployment(self, namespace=None, name=None, deployment=None):
        api_instance = client.AppsV1Api()
        back = api_instance.replace_namespaced_deployment(name=name, namespace=namespace, body=deployment)
        return back
    
    def delete_deployment(self, namespace=None, name=None):
        api_instance = client.AppsV1Api()
        try:
            api_instance.delete_namespaced_deployment(name=name, namespace=namespace, body=client.V1DeleteOptions(propagation_policy="Foreground", grace_period_seconds=5))
        except:
            logging.error(f"delete_deployment error") 

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

    def build_persistentvolumeclaim(self, namespace=None, name=None, storage=None):
        return client.V1PersistentVolumeClaim(
            api_version='v1',
            kind='PersistentVolumeClaim',
            metadata=client.V1ObjectMeta(
                namespace=namespace,
                name=name
            ),
            spec=client.V1PersistentVolumeClaimSpec(
                #storage_class_name='local-path',
                access_modes=[
                    'ReadWriteMany'
                ],
                resources=client.V1ResourceRequirements(
                    requests={
                        'storage': storage
                    }
                )
            )
    )

    def create_persistentvolumeclaim(self, namespace=None, persistentvolumeclaim=None):
        api_instance = client.CoreV1Api()
        try:
            api_instance.create_namespaced_persistent_volume_claim(namespace=namespace, body=persistentvolumeclaim)
        except:
            logging.error(f"create_pvc error") 

    def delete_persistentvolumeclaim(self, namespace=None, name=None):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespaced_persistent_volume_claim(namespace=namespace, name=name)
        except:
            logging.error(f"delete_pvc error") 


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

    def create_persistentvolume(self, persistentvolume=None):
        api_instance = client.CoreV1Api()
        try:
            api_instance.create_persistent_volume(body=persistentvolume)
        except:
            logging.error(f"create_pv error")

    def delete_persistentvolume(self, name=None):
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_persistent_volume(name=name)
        except:
            logging.error(f"delete_pv error")



#Rolebinding

    def build_rolebinding(self, namespace=None):
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

    def create_rolebinding(self, namespace=None, rolebinding=None):
        api_instance = client.RbacAuthorizationV1Api()
        try:
            api_instance.create_namespaced_role_binding(namespace, rolebinding)
        except:
            logging.error(f"create_rolebinding error")

    def delete_rolebinding(self, namespace=None, name='default-admin'):
        api_instance = client.RbacAuthorizationV1Api()
        try:
            api_instance.delete_namespaced_role_binding(name=name, namespace=namespace)
        except:
            logging.error(f"delete_rolebinding error")

