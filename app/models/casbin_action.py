from datetime import datetime
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from utils.database import DBBase


class CasbinAction(DBBase):
    __tablename__ = 'casbin_action'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(128), nullable=False, unique=True, comment='动作名称')
    action_key = Column(String(128), nullable=False, unique=True, comment='动作标识')
    description = Column(String(128), nullable=True, comment='动作描述')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    user = relationship('User', back_populates='casbin_actions')
