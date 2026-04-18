"""
Top-level API v1 router — register all endpoint routers here.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, items, pipeline

api_router = APIRouter()

api_router.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
api_router.include_router(users.router,    prefix="/users",    tags=["Users"])
api_router.include_router(items.router,    prefix="/items",    tags=["Items"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])

