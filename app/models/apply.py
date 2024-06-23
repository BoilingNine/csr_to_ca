from datetime import datetime
from sqlalchemy import Column, Integer, DateTime

from utils.database import DBBase


class Apply(DBBase):
    __tablename__ = 'apply'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='申请ID')
    status = Column(Integer, nullable=False, default=0, comment='0：申请,1:通过，2:拒绝')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    deleted_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment='删除时间')
