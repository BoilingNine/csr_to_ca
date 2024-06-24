import os

from casbin import AsyncEnforcer
from casbin_async_sqlalchemy_adapter import Adapter

from app.models import CasbinRule
from utils.database import engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
adapter = Adapter(engine, db_class=CasbinRule)
model_path = os.path.join(BASE_DIR, 'rbac_model.conf')


async def get_casbin_e():
    """
    get the casbin e object
    :return:
    """
    enforcer = AsyncEnforcer(model_path, adapter)
    await enforcer.load_policy()
    return enforcer
