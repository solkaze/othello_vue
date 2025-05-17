from fastapi import APIRouter
from .ws import router as ws_router
from .rest import router as rest_router

router = APIRouter()
router.include_router(rest_router)
router.include_router(ws_router)