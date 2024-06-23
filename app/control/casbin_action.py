from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.casbin_action import CasbinAction


async def add_casbin_actions(db: AsyncSession, casbin_actions: List[CasbinAction]) -> None:
    """
    add casbin actions to db
    :param db: sqlalchemy session
    :param casbin_actions: casbin actions
    :return: None
    """
    for casbin_action in casbin_actions:
        db.add(casbin_action)
    await db.commit()


async def get_casbin_actions(db: AsyncSession):
    """
    get casbin actions
    :param db: sqlalchemy session
    :return: casbin actions
    """
    res = await db.execute(select(CasbinAction))
    return res.scalars().all()
