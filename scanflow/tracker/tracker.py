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
            logging.error("Scanflow_tracker_uri is not provided")
        if not is_tracker_local_uri_set():
            logging.error("Scanflow_tracker_local_uri is not provided")

        self.verbose = verbose
        check_verbosity(verbose)

    
    def save_app(self, app_name=None, team_name=None, app_dir=None, tolocal=False):
        raise NotImplementedError("tracker:save_app")

    def download_app(self, app_name=None, run_id=None, team_name=None, local_dir=None, fromlocal=False):
        raise NotImplementedError("tracker:download_app")

    def list_app(self):
        raise NotImplementedError("tracker:list_app")

    def search_app(self):
        raise NotImplementedError("tracker:search_app")
    