from scanflow.tools import env

_OUTPUT_DIR_ENV_VAR = "SCANFLOW_WORKFLOW_OUTPUT_DIR"

_output_dir = None

def is_output_dir_set():
    """Returns True if the ouputdir  has been set, False otherwise."""
    if _output_dir or env.get_env(_OUTPUT_DIR_ENV_VAR):
        return True
    return False

def set_output_dir(dir: str) -> None:
    """
      Set the output dir
    """
    global _output_dir
    _output_dir = dir

def get_output_dir() -> str:
    """
        Get the current workflow output dir
    """
    global _output_dir
    if _output_dir is not None:
        return _output_dir
    elif env.get_env(_OUTPUT_DIR_ENV_VAR) is not None:
        return env.get_env(_OUTPUT_DIR_ENV_VAR)
    else:
        return None