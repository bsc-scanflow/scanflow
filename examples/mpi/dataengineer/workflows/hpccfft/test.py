import yaml
import json
with open("hpccfft.yaml", 'r') as yaml_in, open("hpccfft.json", "w") as json_out:
    yaml_object = yaml.safe_load(yaml_in) # yaml_object will be a list or a dict
    print(type(yaml_object))
    
    volumestr = [{'mountPath': '/home', 'volumeClaimName': 'hpccfft'}]
    yaml_object['spec']['volumes'] = volumestr
    
    print(yaml_object['spec']['volumes'])
    json.dump(yaml_object, json_out)
    json_obj = json.dumps(yaml_object)
    print(json_obj)