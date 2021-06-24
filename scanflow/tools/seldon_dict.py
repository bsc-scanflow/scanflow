def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}


def verify_dict(d):
    try:
        spec = d['spec']['predictors'][0]['componentSpecs'][0]['spec']
        if spec is not None:
            for container in spec['containers']:
                container_dict = {}
                for k, v in container.items():
                    if k == 'volume_mounts':
                        vms = []
                        for volumeMount in v:
                            vm = {}
                            vm.update(mountPath = volumeMount['mount_path']) 
                            vm.update(name = volumeMount['name'])
                            vms.append(vm)
                        container_dict.update(volumeMounts = vms)
                container.update(container_dict)
            volumes = []
            for volume in spec['volumes']:
                vol = {}
                vol.update(name = volume['name'])
                volume['persistent_volume_claim'].update(
                            claimName = volume['persistent_volume_claim']['claim_name']
                        )
                vol.update(persistentVolumeClaim = 
                        volume['persistent_volume_claim'])
                volumes.append(vol)
            spec.update(volumes = volumes)
    except:
        pass
    
    return d
    
