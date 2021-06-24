#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

monitor_rules_router = APIRouter(tags=['monitor rules'])

@monitor_rules_router.get("/",
                            status_code= status.HTTP_200_OK)
async def rules_root():
    print(f"Hello! monitor rules")
    return {"Hello": "monitor rules"}

