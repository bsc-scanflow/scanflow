# -*- coding: utf-8 -*-

# Author: Gusseppe Bravo
# License: BSD 3 clause

import os
import mlflow

from pathlib import Path


def list_artifacts(run_id=None):
    tracker_dir = "/mlflow/"
    tracker_uri = f'file://{tracker_dir}/mlruns/'

    tracker = mlflow.tracking.MlflowClient(tracking_uri=tracker_uri)

    if run_id is None: # Return the last experiment run
        exp_dir = os.path.join(tracker_dir, "mlruns/0")
        paths = sorted(Path(exp_dir).iterdir(), key=os.path.getmtime, reverse=True)
        run_id = os.path.basename(str(paths[0]))

    run = tracker.get_run(run_id)

    artifact_dir = run.info.artifact_uri.replace('/mlflow', tracker_dir)

    artifacts = {artifact : os.path.join(artifact_dir, artifact)
                 for artifact in os.listdir(artifact_dir)}

    return artifacts

def get_tracked_values(executor_name=None, verbose=False, **args):
    """
        This function will provide all the tracked values for each workflow.

        For search syntax see: https://www.mlflow.org/docs/latest/search-syntax.html
    """
    tracker_dir = "/mlflow/"
    if tracker_dir is not None:
        # tracker_uri = f'file://{tracker_dir}/mlruns/'
        tracker_uri = f'file://{tracker_dir}/mlruns/'
        mlflow.set_tracking_uri(tracker_uri)
        df = mlflow.search_runs(['0'], **args) # By now use this because of dataframe output
        col_executor_name = 'tags.mlflow.runName'
        if verbose:
            try:
                if executor_name is not None:

                    return df[df[col_executor_name] == executor_name]
                else:
                    return df
            except KeyError as e:
                logging.error(f"{e}")
                logging.warning(f"There is no executor with name: {executor_name}.")
        else:
            not_cols = ['experiment_id', 'status',
                        'artifact_uri', 'tags.mlflow.source.type',
                        'tags.mlflow.user']

            try:
                if executor_name is not None:
                    return df[df.columns.difference(not_cols)][df[col_executor_name] == executor_name]
                else:
                    return df[df.columns.difference(not_cols)]
            except KeyError as e:
                logging.error(f"{e}")
                logging.warning(f"There is no executor with name: {executor_name}.")
    else:
        print(f"There is no metadata for {workflow_name}.")

        return None
    

