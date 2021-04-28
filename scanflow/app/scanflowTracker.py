

class Tracker():
    def __init__(self,
                 nodePort: int,
                 image: str = "172.30.0.49:5000/scanflow-tracker"):
        
        self.image = image
        self.nodePort = nodePort