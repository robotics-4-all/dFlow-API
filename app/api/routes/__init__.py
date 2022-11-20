from fastapi import APIRouter
from app.api.routes.user import router as user_router
from app.api.routes.dflow import router as dflow_router


router = APIRouter()

router.include_router(user_router, tags=["user"])
router.include_router(dflow_router, tags=["dsl"])
