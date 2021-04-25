import yaml
import couler.argo as couler
from couler.argo_submitter import ArgoSubmitter
from couler.core.templates.volume import VolumeMount, Volume


import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class ArgoWorkflows:
    def __init__(self,
                 k8s_config_file=None,
                 verbose=True):
        self.verbose = verbose
        # if not provide config_file, couler internally uses in_cluster_config
        self.k8s_config_file = k8s_config_file

    def submitWorkflow(self, namespace=None):
        if self.k8s_config_file is not None:
            submitter = ArgoSubmitter(namespace, self.k8s_config_file)
        else:
            submitter = ArgoSubmitter(namespace)
        couler.run(submitter=submitter)

    def deleteWorkflow(self, namespace=None, name=None):
        if self.k8s_config_file is not None:
            couler.delete(name=name, namespace=namespace, config_file=self.k8s_config_file)
        else:
            couler.delete(name=name, namespace=namespace)

    def buildVolumes(self, **kwargs):
        for k, v in kwargs.items():
            volume = Volume( k, v)
            couler.add_volume(volume)

    def buildVolumeMounts(self, **kwargs):
        volumeMounts = []
        for k, v in kwargs.items():
            volumeMount = VolumeMount(k, v)
            volumeMounts.append(volumeMount)
        return volumeMounts

    def buildDagTask(self, name, image, env, volumeMounts, dependencies):
        couler.set_dependencies(
            lambda: couler.run_container(
                step_name=name,
                image=image,
                env=env,
                volume_mounts=volumeMounts,
            ), 
            dependencies=dependencies
        )

