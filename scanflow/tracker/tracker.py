"""
abstract tracker class
"""
import logging

from scanflow.tools.scanflowtools import check_verbosity
from scanflow.tracker.utils import (
    set_tracker_uri,
    set_tracker_local_uri,
    is_tracker_local_uri_set,
    is_tracker_uri_set,
    get_tracker_uri,
)


logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

class Tracker():
    def __init__(self,
                 scanflow_tracker_uri=None,
                 scanflow_tracker_local_uri=None,
                 verbose=True):
        #scanflow_tracker_uri
        if scanflow_tracker_uri is not None:
            set_tracker_uri(scanflow_tracker_uri)
        #scanflow_tracker_local_uri
        if scanflow_tracker_local_uri is not None:
            set_tracker_local_uri(scanflow_tracker_local_uri)

        if not is_tracker_uri_set():
            logging.info("Scanflow_tracker_uri is not provided")
        if not is_tracker_local_uri_set():
            logging.info("Scanflow_tracker_local_uri is not provided")
        
        if (not is_tracker_local_uri_set() and not is_tracker_uri_set):
            raise EnvironmentError("NO SCANFLOW TRACKER FOUND")

        self.verbose = verbose
        check_verbosity(verbose)

    def get_tracker_uri(self, islocal=True):
        return get_tracker_uri(islocal)

    #develop artifacts
    def save_app_artifacts(self, app_name, team_name, app_dir="/workflow", tolocal=False):
        raise NotImplementedError("tracker:save_app")

    def download_app_artifacts(self, app_name, run_id=None, team_name=None, local_dir="/workflow", fromlocal=False):
        raise NotImplementedError("tracker:download_app")

    # model
    def save_app_model(self, app_name, team_name, model_name):
        raise NotImplementedError("tracker: save model")

    def download_app_model(self, app_name, team_name, model_name, model_version):
        raise NotImplementedError("tracker: download model")

    # meta-data
    def save_app_meta(self, app):
        raise NotImplementedError("tracker: save app meta")

    def download_app_meta(self, app_name, team_name):
        raise NotImplementedError("tracker: download app meta")
 
#    def list_app_meta(self):
#        raise NotImplementedError("tracker:list_app")
#
#    def search_app_meta(self):
#        raise NotImplementedError("tracker:search_app")
    