from fastapi import APIRouter

from app.api import csr, user

api = APIRouter(prefix='/api',
                dependencies=[])
api.include_router(user.router)
api.include_router(csr.router)

