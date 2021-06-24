import sys
import matplotlib.pyplot as plt
import os
sys.path.insert(0,'../..')

import scanflow
from scanflow.client import ScanflowTrackerClient

# App folder
scanflow_path = "/gpfs/bsc_home/xpliu/pv/jupyterhubpeini/scanflow"
app_dir = os.path.join(scanflow_path, "examples/mnist/data")
app_name = "mnist"
team_name = "data"

# scanflow client
client = ScanflowTrackerClient(scanflow_tracker_uri="http://172.30.0.50:46667",
                        verbose=True)

                
client.save_artifacts(app_name=app_name, 
                      team_name=team_name, 
                      app_dir=app_dir)

client.download_artifacts(app_name=app_name, 
      local_dir="/gpfs/bsc_home/xpliu/pv/jupyterhubpeini/scanflow/tutorials/mnist")
client.download_artifacts(app_name=app_name, 
      team_name="data",
      local_dir="/gpfs/bsc_home/xpliu/pv/jupyterhubpeini/scanflow/tutorials/mnist")
client.download_artifacts(app_name="mnist", 
      run_id="aadd04288ed94baf804232a8a6ae0665",
      local_dir="/gpfs/bsc_home/xpliu/pv/jupyterhubpeini/scanflow/tutorials/mnist")
    

client.save_artifacts(app_name=app_name, 
      team_name="data", 
      app_dir=app_dir,
      tolocal=True)

client.download_artifacts(app_name=app_name, 
                    team_name="data",
                    local_dir="/gpfs/bsc_home/xpliu/pv/jupyterhubpeini/scanflow/tutorials/mnist",
                   fromlocal=True)