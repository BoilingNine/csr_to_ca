from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


async def create_role(db: AsyncSession, role: Role):
    """
    create new role
    :param db: sqlalchemy session
    :param role: role instance
    :return: None
    """
    db.add(role)
    await db.commit()


async def get_role_by_role_key(db: AsyncSession, role_key: str):
    """
    get role by role key
    :param db: SQLAlchemy session
    :param role_key:role key
    :return:role instance
    """
    res = await db.execute(select(Role).filter_by(role_key=role_key))
    return res.scalar()
