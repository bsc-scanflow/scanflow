from scanflow.tools import env

_SERVER_URI_ENV_VAR = "SCANFLOW_SERVER_URI"

_server_uri = None

def is_server_uri_set():
    """Returns True if the server URI has been set, False otherwise."""
    if _server_uri or env.get_env(_SERVER_URI_ENV_VAR):
        return True
    return False

def set_server_uri(uri) -> None:
    """
      Set the server URI. 
    """
    global _server_uri
    _server_uri = uri

def get_server_uri() -> str:
    """
        Get the current tracker server uri
    """
    global _server_uri
    if _server_uri is not None:
        return _server_uri
    elif env.get_env(_SERVER_URI_ENV_VAR) is not None:
        return env.get_env(_SERVER_URI_ENV_VAR)
    else:
        return None