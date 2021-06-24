from scanflow.tools import env

_TRACKER_URI_ENV_VAR = "SCANFLOW_TRACKER_URI"
_TRACKER_LOCAL_URI_ENV_VAR = "SCANFLOW_TRACKER_LOCAL_URI"

_tracker_uri = None
_tracker_local_uri = None

def is_tracker_uri_set():
    """Returns True if the tracking URI has been set, False otherwise."""
    if _tracker_uri or env.get_env(_TRACKER_URI_ENV_VAR):
        return True
    return False

def is_tracker_local_uri_set():
    """Returns True if the tracking URI has been set, False otherwise."""
    if _tracker_local_uri or env.get_env(_TRACKER_LOCAL_URI_ENV_VAR):
        return True
    return False

def set_tracker_uri(uri) -> None:
    """
       Set the tracker server URI. 
    """
    global _tracker_uri
    _tracker_uri = uri

def set_tracker_local_uri(uri) -> None:
    """
       Set the tracker local server URI. 
    """
    global _tracker_local_uri
    _tracker_local_uri = uri

def get_tracker_uri(islocal=False) -> str:
    """
        Get the current tracker server uri
    """
    global _tracker_uri
    global _tracker_local_uri
    if islocal:
        if _tracker_local_uri is not None:
            return _tracker_local_uri
        elif env.get_env(_TRACKER_LOCAL_URI_ENV_VAR) is not None:
            return env.get_env(_TRACKER_LOCAL_URI_ENV_VAR)
        else:
            return None
    else:
        if _tracker_uri is not None:
            return _tracker_uri
        elif env.get_env(_TRACKER_URI_ENV_VAR) is not None:
            return env.get_env(_TRACKER_URI_ENV_VAR)
        else:
            return None