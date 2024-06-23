from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from utils.database import DBBase


class User(DBBase):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(32), nullable=False, unique=True, comment='账号')
    hashed_password = Column(String(128), nullable=False, comment='用户密码')
    nickname = Column(String(32), nullable=False, comment='用户昵称')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    deleted_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment='删除时间')
    roles = relationship('Role', uselist=True, back_populates='user')
    casbin_objects = relationship('CasbinObject', uselist=True, back_populates='user')
    casbin_actions = relationship('CasbinAction', uselist=True, back_populates='user')
