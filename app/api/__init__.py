from fastapi import APIRouter

from app.api import csr_to_ca,signature

api = APIRouter(prefix='/api',
                dependencies=[])
api.include_router(csr_to_ca.router)
api.include_router(signature.router)

