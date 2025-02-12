from enum import Enum
from typing import Optional


def to_enum(enum_class: type, value: str) -> Optional[Enum]:
    if isinstance(value, enum_class):
        return value
    str_value = str(value)
    if str_value in enum_class._value2member_map_:
        return enum_class(str_value)
    return None
