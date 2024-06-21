from fastapi import APIRouter

from app.api import csr

api = APIRouter(prefix='/api',
                dependencies=[])

api.include_router(csr.router)
