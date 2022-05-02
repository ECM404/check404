import ctypes
from collections import namedtuple
from typing import Any, Optional, List

FuncTypes = namedtuple("FuncTypes", ["restype", "argtypes"])
c_any = Any


def parse_types(types: List) -> FuncTypes:
    res, args = types
    argtypes = []
    restype = parse_type(res)
    for arg in args:
        argtypes.append(parse_type(arg))
    return FuncTypes(restype, argtypes)


def parse_type(type_name: str) -> Any:
    if is_pointer(type_name):
        restype = ctypes.POINTER(getattr(ctypes, type_name[1:]))
    elif is_array(type_name):
        c_type, qty = type_name.split(",")
        restype = getattr(ctypes, c_type) * int(qty)
    else:
        restype = getattr(ctypes, type_name)
    return restype


def get_args(inputs: Optional[List], argtypes: List[c_any]) -> List[c_any]:
    """Get all input arguments from c_types list
    """
    if inputs is None:
        inputs = []
    arglist = []
    for input, argtype in zip(inputs, argtypes):
        arglist.append(get_arg(input, argtype))
    return arglist


def get_arg(input: Any, c_type: c_any) -> c_any:
    """Get single argument from c_type
    """
    return c_type(input)


def is_pointer(type_name: str) -> bool:
    """Checks if type is pointer. Returns True or False.
    """
    return type_name[0] == "*"


def is_array(type_name: str) -> bool:
    """Checks if type is array. Returns True or False.
    """
    return "," in type_name
