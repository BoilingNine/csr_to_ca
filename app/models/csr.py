from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from utils.database import DBBase


class CSR(DBBase):
    __tablename__ = 'csr'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='csr_ID')
    file_name = Column(String(255), nullable=False, unique=True, comment='文件名')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='创建者')
    country_name = Column(String(255), nullable=False, comment='国家')
    state_or_province_name = Column(String(255), nullable=False, comment='洲或省')
    locality_name = Column(String(255), nullable=False, comment='市')
    organization_name = Column(String(255), nullable=False, comment='组织名称')
    common_name = Column(String(255), nullable=False, comment='公共名称')
    dns_name = Column(String(255), nullable=False, comment='主题备用名称扩展')
    status = Column(Integer, nullable=False, default=0, comment='0：待审核,1:通过，2:拒绝')
