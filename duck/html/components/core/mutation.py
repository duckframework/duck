"""
Module that keeps track of components mutation.
"""

import enum

from typing import Dict, Any


class MutationCode(enum.IntEnum):
    # Global mutation
    SET_INNER_HTML = -1
    
    # Child mutation
    DELETE_CHILD = 0x0
    INSERT_CHILD = 0x1
    
    # Props mutation
    DELETE_PROP = 0x2
    SET_PROP = 0x3
    
    # Style mutation
    DELETE_STYLE = 0x4
    SET_STYLE = 0x5
    

class Mutation:
    """
    Mutation class to represent mutations.
    """
    
    __slots__ = ("target", "code", "payload")
    
    def __init__(
        self,
        target,
        code: MutationCode,
        payload: Dict[Any, Any],
    ) -> None:
        self.target = target
        self.code = code
        self.payload = payload
    
    def __repr__(self):
        return (
            f"<[{self.__class__.__name__} \n"
            f"  code={repr(self.code)}, \n"
            f"  payload={self.payload}, \n"
            f"  target={self.target},\n"
            "]>"
        )[:]

    __str__ = __repr__


def on_mutation(target, mutation: Mutation):
    """
    Entry function to be executed when a mutation happens.
    
    Notes:
    - Every mutation is propagated in the following order:
        ```
        target -> parent (if available) -> components in between -> root (if available)
        ```
    """
    target._on_mutation(mutation)
    
    if not target.isroot():
        target.traverse_ancestors(lambda a: a._on_mutation(mutation), include_self=False)
