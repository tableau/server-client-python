"""Target class meant to abstract mappings to other objects"""
from typing import TypeVar

T = TypeVar('T', bound='Target')


class Target():
    def __init__(self, id_: str, target_type: str) -> None:
        self.id = id_
        self.type = target_type
        return

    def __repr__(self):
        return "<Target#{id}, {type}>".format(**self.__dict__)
