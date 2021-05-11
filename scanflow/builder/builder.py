from scanflow.app import Application, Executor, Workflow
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
        # 2. build scanflow workflows - executors
        """
        raise NotImplementedError("build_ScanflowApplication is not implemented")
    
    def build_ScanflowExecutor(self, executor: Executor):

        raise NotImplementedError("build_scanflow executor is not implemented")