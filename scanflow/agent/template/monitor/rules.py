#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException

monitor_rules_router = APIRouter(tags=['monitor rules'])

@monitor_rules_router.get("/",
                            status_code= status.HTTP_200_OK)
async def rules_root():
    print(f"Hello! monitor rules")
    return {"Hello": "monitor rules"}

from scanflow.agent.template.monitor.actuators import analyze_number_of_pictures

def rule_number_of_pictures(number_of_pictures: int):
    if number_of_pictures > 20:
        analyze_number_of_pictures(number_of_pictures)