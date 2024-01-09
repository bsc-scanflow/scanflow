

class Tracker():
    def __init__(self,
                 nodePort: int,
                 image: str = "registry.gitlab.bsc.es/datacentric-computing/cloudskin-project/cloudskin-registry/scanflow-tracker"):
        
        self.image = image
        self.nodePort = nodePort