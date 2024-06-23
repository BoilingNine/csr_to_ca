from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.casbin_rule import CasbinRule


async def add_casbin_rule(db: AsyncSession, casbin_rule: CasbinRule):
    """
    Add a casbin_rule
    :param db: SQLAlchemy Session
    :param casbin_rule: casbin_rule object
    :return:
    """
    db.add(casbin_rule)
    await db.commit()


async def filter_casbin_rule(db: AsyncSession, casbin_rule: CasbinRule):
    """
    Filter casbin_rule
    :param db: sqlalchemy session
    :param casbin_rule: casbin_rule instance
    :return:
    """
    res = await db.execute(select(CasbinRule).filter_by(ptype=casbin_rule.ptype, v0=casbin_rule.v0, v1=casbin_rule.v1,
                                                        v2=casbin_rule.v2))
    return res.first()


async def create_casbin_rules(db: AsyncSession, casbin_rules: List[CasbinRule]):
    """
    Create casbin_rules
    :param db: SQLAlchemy session
    :param casbin_rules: CasbinRole instances
    :return: int
    """
    k = 0
    for casbin_rule in casbin_rules:
        x = await filter_casbin_rule(db, casbin_rule)
        if x:
            k += 1
        else:
            await add_casbin_rule(db, casbin_rule)
    return k


async def filter_casbin_rule_g(db: AsyncSession, casbin_rule):
    """
    filter CasbinRole
    :param db: SQLAlchemy session
    :param casbin_rule:
    :return:
    """
    res = await db.execute(select(CasbinRule).filter_by(ptype=casbin_rule.ptype, v0=casbin_rule.v0, v1=casbin_rule.v1))
    return res.all()


async def create_casbin_rule_g(db: AsyncSession, casbin_rule_g):
    """
    Add a casbin rule g
    :param db: sqlalchemy Session
    :param casbin_rule_g: casbin_rule_g object
    :return:
    """

    k = await filter_casbin_rule_g(db, casbin_rule_g)
    if k:
        return k.count()
    else:
        await add_casbin_rule(db, casbin_rule_g)
        return 0
