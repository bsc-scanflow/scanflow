from pydantic import BaseModel, Field, PyObject, AnyHttpUrl
from typing import Optional, List, Dict, Any

class RequestData(BaseModel):
    args: Optional[tuple] = None
    kwargs: Optional[Dict[str, Any]] = None