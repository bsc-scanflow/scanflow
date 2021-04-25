from pydantic import BaseModel

class ResponseMessageBase(BaseModel):
    status: int

class More(ResponseMessageBase):
    pass

