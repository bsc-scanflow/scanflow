#fastapi
from fastapi import Depends
#scanflow
from scanflow.client import ScanflowTrackerClient

async def get_tracker():
    client = ScanflowTrackerClient(verbose=True)
    try:
        yield client
    finally:
        logging.info("Connecting tracking server uri: {}".format(client.get_tracker_uri(False)))