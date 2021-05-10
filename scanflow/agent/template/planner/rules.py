#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

planner_rules_router = APIRouter(tags=['planner rules'])

@planner_rules_router.get("/",
                            status_code= status.HTTP_200_OK)
async def rules_root():
    print(f"Hello! planner rules")
    return {"Hello": "planner rules"}