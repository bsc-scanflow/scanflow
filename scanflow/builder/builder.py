from scanflow.app import Application, Node, Workflow, Agent
class Builder():
    def __init__(self,
                 registry: str):
        """
          builder is used to generate image from the source code user provided and submit the meta data to scanflow server
        """
        self.registry = registry

    def build_ScanflowApplication(self, app: Application, trackerPort: int):
        """
        # 1. build scanflow agent
        # 2. build scanflow workflows - nodes
        """
        raise NotImplementedError("build_ScanflowApplication is not implemented")

    def build_ScanflowWorkflow(self, workflow: Workflow):
        raise NotImplementedError("build_scanflow workflow is not implemented")
    
    def build_ScanflowNode(self, node: Node):
        raise NotImplementedError("build_scanflow node is not implemented")

    def build_ScanflowAgent(self, agent: Agent):
        raise NotImplementedError("build_scanflow agent is not implemented")