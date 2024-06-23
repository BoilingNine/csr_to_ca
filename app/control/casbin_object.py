from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.casbin_object import CasbinObject


async def add_casbin_objects(db: AsyncSession, casbin_objects):
    """
    add casbin objects
    :param db: sqlalchemy session
    :param casbin_objects: casbin objects
    :return: None
    """
    for casbin_object in casbin_objects:
        db.add(casbin_object)
    await db.commit()


async def get_casbin_objects(db: AsyncSession):
    """
    get casbin objects
    :param db: sqlalchemy session
    :return: casbin objects
    """
    res = await db.execute(select(CasbinObject))
    return res.scalars().all()
