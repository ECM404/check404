from __future__ import annotations
import ctypes
from typing import Any, Tuple

c_any = Any

TYPE_MAP = {
    "int": ctypes.c_int,
    "float": ctypes.c_float,
    "double": ctypes.c_double,
    "char*": ctypes.c_wchar_p,
    "char": ctypes.c_wchar
    }


def parse_function(function_string: str) -> Tuple:
    """Function that takes a c declaration and extracts:
        * Return type
        * Function name
        * Argument types

    Returns everything in a Tuple
    """
    open_par_index = function_string.find('(')
    closing_par_index = function_string.find(')')
    before_par = function_string[:open_par_index]
    inside_par = function_string[open_par_index + 1:closing_par_index]
    return_type, function_name = before_par.split()
    argument_types = inside_par.replace(" ", "").split(",")
    return return_type, function_name, argument_types


def get_args(c_arg_types: c_any, check_in: list) -> list:
    out = []
    for c_arg_type, check_input in zip(c_arg_types, check_in):
        if isinstance(check_input, list):
            out.append(c_arg_type(*check_input))
        else:
            out.append(c_arg_type(check_input))
    return out


def parse_ctype(type_str: str) -> c_any:
    """Function that takes a string definition of a type and maps it to its
    adequate c_type.
    """
    # First, we check if it is an array
    if "[" in type_str:
        base_type = type_str[:type_str.find("[")]
        arr_size = int(type_str[type_str.find("[")+1:type_str.find("]")])
        return TYPE_MAP[base_type] * arr_size
    return TYPE_MAP[type_str]
