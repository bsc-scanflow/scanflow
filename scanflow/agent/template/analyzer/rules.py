#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

analyzer_rules_router = APIRouter(tags=['analyzer rules'])

@analyzer_rules_router.get("/",
                            status_code= status.HTTP_200_OK)
async def rules_root():
    print(f"Hello! analyzer rules")
    return {"Hello": "analyzer rules"}