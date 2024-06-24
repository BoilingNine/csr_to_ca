from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSR
from app.schemas.usr import UserBase


async def add_csr(db: AsyncSession, csr: CSR) -> CSR:
    """"
    Add a CSR
    """
    db.add(csr)
    await db.commit()
    await db.refresh(csr)
    return csr


async def get_csr_list_from_db(db: AsyncSession, user: UserBase):
    """"
    Get a list of csr
    """
    res = await db.execute(select(CSR).filter_by(user_id=user.id).order_by(CSR.create_time))
    return res.scalars().all()


async def check_csr_db(db: AsyncSession, scr_id: int, status: int):
    res = await db.execute(select(CSR).filter_by(id=scr_id))
    res.scalar().status = status
    await db.commit()



async def get_csr_db(db: AsyncSession, scr_id: int):
    res = await db.execute(select(CSR).filter_by(id=scr_id))
    return res.scalar()

