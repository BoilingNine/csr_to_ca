import asyncio
import os
from casbin_async_sqlalchemy_adapter import Adapter

from app.control.casbin_action import add_casbin_actions, get_casbin_actions
from app.control.casbin_object import add_casbin_objects, get_casbin_objects
from app.control.casbin_rule import create_casbin_rules, create_casbin_rule_g
from app.control.role import create_role, get_role_by_role_key
from app.control.user import add_user, get_user_by_username
from app.models.casbin_action import CasbinAction
from app.models.casbin_object import CasbinObject
from app.models.casbin_rule import CasbinRule
from app.models.role import Role
from app.models.user import User
from utils.database import engine, SessionLocal
from utils.utils import gen_password_hash

base_dir = os.path.dirname(os.path.abspath(__file__))

session = SessionLocal()
adapter = Adapter(engine, db_class=CasbinRule)


class TestDatabase:
    def __init__(self):
        self.session = session
        self.adapter = adapter

    async def init_db(self):

        # 创建用户
        hashed_password = await gen_password_hash('123456')
        await add_user(self.session, User(nickname='admin', username='admin', hashed_password=hashed_password))
        user = await get_user_by_username(self.session, "admin")
        # 创建角色role
        await create_role(self.session,
                          Role(name='管理员', role_key='admin', description='管理权限', user=user))
        await create_role(self.session,
                          Role(name='普通用戶', role_key='common', description='普通用户', user=user))
        # # 创建CasbinAction
        casbin_actions = [
            CasbinAction(name='审核', action_key='check', description='审核', user=user),
        ]
        await add_casbin_actions(self.session, casbin_actions)

        # 创建CasbinObject
        casbin_objects = [
            CasbinObject(name='申请', object_key='CSR', description='Apply表--用户申请', user=user),
        ]
        await add_casbin_objects(self.session, casbin_objects)
        # 设置管理员
        role = await get_role_by_role_key(self.session, "admin")  # 管理员组
        casbin_actions = await get_casbin_actions(self.session)  # 动作
        casbin_objects = await get_casbin_objects(self.session)  # 资源
        casbin_roles = []
        for casbin_object in casbin_objects:
            for casbin_action in casbin_actions:
                casbin_roles.append(CasbinRule(ptype='p', v0=role.role_key,
                                               v1=casbin_object.object_key, v2=casbin_action.action_key))
        # 为管理员增加所有policy
        k = await create_casbin_rules(self.session, casbin_roles)
        assert k == 0

        # 设置用户admin的角色为管理员
        k = await create_casbin_rule_g(self.session, CasbinRule(ptype='g', v0=user.username, v1="admin"))
        assert k == 0


if __name__ == "__main__":
    database = TestDatabase()
    asyncio.run(database.init_db())
