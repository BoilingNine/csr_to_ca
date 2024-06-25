from enum import Enum
from types import DynamicClassAttribute

USER_NAME_MIN = 1
USER_NAME_MAX = 32
USER_NICKNAME_MIN = 1
USER_NICKNAME_MAX = 32
PASSWORD_MIN = 5
PASSWORD_MAX = 12

# 分页
PAGE_INDEX = 1
PAGE_NUM = 10
PAGE_TOTAL = 0


# 为Pydantic定义枚举值类
class EBase(Enum):
    @classmethod
    def __init__(cls):
        cls.values = {}

    def __repr__(self):
        return f'"{self._value_}"'

    def __str__(self):
        return f'"{self._value_}"'

    @DynamicClassAttribute
    def cname(self):
        """ 返回中文名称"""
        return self.values.get(self.value)

    @classmethod
    def fmt(cls):
        """
        将枚举值及代表含义格式化
        :return:
        :rtype:
        """
        ret = []
        for m in cls._value2member_map_.keys():
            ret.append(f'{m}:{cls.values.get(m)}')
        return f'{cls.__doc__}  {", ".join(ret)}'


