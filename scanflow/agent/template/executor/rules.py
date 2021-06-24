#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

executor_rules_router = APIRouter(tags=['executor rules'])

@executor_rules_router.get("/",
                            status_code= status.HTTP_200_OK)
async def rules_root():
    print(f"Hello! executor rules")
    return {"Hello": "executor rules"}