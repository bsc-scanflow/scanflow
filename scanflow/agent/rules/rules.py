from fastapi import FastAPI, APIRouter
from scanflow.agent.config.settings import settings

rules_router = APIRouter(prefix="/rules")

if settings.AGENT_TYPE == "monitor":
    from scanflow.agent.template.monitor import rules
    rules_router.include_router(rules.monitor_rules_router)
elif settings.AGENT_TYPE == "analyzer":
    from scanflow.agent.template.analyzer import rules
    rules_router.include_router(rules.analyzer_rules_router)
elif settings.AGENT_TYPE == "planner":
    from scanflow.agent.template.planner import rules
    rules_router.include_router(rules.planner_rules_router)
elif settings.AGENT_TYPE == "executor":
    from scanflow.agent.template.executor import rules
    rules_router.include_router(rules.executor_rules_router)
else:
    #custom agent rules
    from scanflow.agent.rules import custom_rules
    rules_router.include_router(rules.custom_rules_router)
