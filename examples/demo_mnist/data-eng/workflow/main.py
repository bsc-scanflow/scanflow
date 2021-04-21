import os
path = '/'
#os.chdir(path)

import sys
sys.path.append(path)

from scanflow.setup import setup
from scanflow.run import run

# App folder
app_dir = '//examples/leaf_ds_compose'

# Workflows
workflow1 = [
    {'name': 'gathering_1', 'file': 'gathering.py',
            'env': 'gathering_1'},

    {'name': 'preprocessing_1', 'file': 'preprocessing.py',
            'env': 'preprocessing_1'},

]
workflow2 = [
    {'name': 'modeling_1', 'file': 'modeling.py',
            'env': 'modeling_1'},


]
workflows = [
    {'name': 'workflow1', 'workflow': workflow1, 'tracker': {'port': 8001}},
    {'name': 'workflow2', 'workflow': workflow2, 'tracker': {'port': 8002}}

]

workflow_datascience = setup.Setup(app_dir, workflows)


# Read the platform
runner = run.Run(workflow_datascience)

# Run the workflow
runner.run_workflows()
