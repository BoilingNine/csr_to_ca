from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSR


async def add_csr(db: AsyncSession, csr: CSR) -> CSR:
    """"
    Add a CSR
    """
    db.add(csr)
    await db.commit()
    await db.refresh(csr)
    return csr