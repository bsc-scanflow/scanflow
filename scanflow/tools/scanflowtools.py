import os
import logging
import json

def get_scanflow_paths(app_dir):
    # 1. save workflow defined by user
    workflows_dir = os.path.join(app_dir, 'workflows')
    # 2. start template agent inside, and user modify the agents
    agents_dir = os.path.join(app_dir, 'agents')
    # 3. meta data generated by scanflow(for example, workflow.json) 
    meta_dir = os.path.join(app_dir, 'meta')
    deploy_dir = os.path.join(meta_dir, 'deploy')#maybe generate app

    paths = {'app_dir': app_dir,
             'workflows_dir': workflows_dir,
             'agents_dir': agents_dir,
             'meta_dir': meta_dir,
             'deploy': deploy_dir}

    return paths

def check_verbosity(verbose):
    logger = logging.getLogger()
    if verbose:
        logger.disabled = False
    else:
        logger.disabled = True

def save_workflows(paths, workflows):
    meta_dir = paths['meta_dir']

    workflows_metadata_name = 'workflows.json'
    workflows_metadata_path = os.path.join(meta_dir, workflows_metadata_name)

    with open(workflows_metadata_path, 'w') as fout:
        json.dump(workflows, fout)


def read_workflows(paths):
    meta_dir = paths['meta_dir']

    workflows_metadata_name = 'workflows.json'
    workflows_metadata_path = os.path.join(meta_dir, workflows_metadata_name)

    try:
        with open(workflows_metadata_path) as fread:
            data = json.load(fread)

        return data

    except ValueError as e:
        logging.error(f"{e}")
        logging.error(f"[-] Workflows metadata has not yet saved.")
