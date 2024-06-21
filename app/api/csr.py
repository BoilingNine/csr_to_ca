from fastapi import APIRouter

from app.schemas.schemas import BaseRsp

router = APIRouter(
    prefix="/casbin/v1",
    tags=["用户管理"]
)


@router.get('/get_menu', summary="生成csr文件", response_model=BaseRsp)
async def api_get_menu_permissions():
    return BaseRsp()
