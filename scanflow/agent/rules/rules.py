from fastapi import FastAPI, APIRouter

rules_router = APIRouter()

@rules_router.get("/")
def rules_root():
    return {"Hello": "rules"}