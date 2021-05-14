from pydantic import BaseModel, Field, PyObject, AnyHttpUrl
from typing import Optional, List, Dict, Any

class Request(BaseModel):
    run_ids: List[str]
    args: Optional[tuple] = None
    kwargs: Optional[Dict[str, Any]] = None