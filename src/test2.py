# from typing import List
# from pydantic import BaseModel, Field

# import OpenHosta.core
# from OpenHosta import config
# from OpenHosta.emulate import emulate

# config.set_default_apiKey("")

# def multiply(a:int, b:int)->int:
#     """
#     This function multiplies two integers in parameter.
#     """
#     return emulate()

# def random_list(size:int)->List[int]:
#     """
#     This function returns a list of random integers of the size in parameter.
#     """
#     return emulate()

# class User(BaseModel):
#     name:str = Field(description="The full name of the user.")
#     age:int = Field(default=0, description="The age of the user. Default if older than 25.")
#     mail:str = Field(description="The email of the user. Must end with \"gmail.com\".")
#     friends:List[str] = Field(default_factory=list, description="A list of the user's friends first names.")

# def fill_user_infos()->User:
#     """
#     This function fill the pydantic model with a randomly generated user.
#     """
#     return emulate()

# res1 = multiply(5, 6)
# print(res1)
# print(type(res1))
# print()

# res2 = random_list(5)
# print(res2)
# print(type(res2))
# print()

# res3 = fill_user_infos()
# print(res3)
# print(type(res3))
# print()

# from types import NoneType
# from typing import get_args, get_origin
# from typing import List, Any, Union

# def convert_to_type(data, type):
#         convert = {
#             NoneType: lambda x: None,
#             Any: lambda x: x,
#             str: lambda x: str(x),
#             int: lambda x: int(x),
#             float: lambda x: float(x),
#             list: lambda x: list(x),
#             set: lambda x: set(x),
#             frozenset: lambda x: frozenset(x),
#             tuple: lambda x: tuple(x),
#             bool: lambda x: bool(x),
#             dict: lambda x: dict(x),
#             complex: lambda x: complex(x),
#             bytes: lambda x: bytes(x),
#         }
#         origin = get_origin(type)
#         args = get_args(type)

#         if origin is not None:
#             if origin in convert:
#                 convert_function = convert[origin]
#                 return convert_function(convert_to_type(d, args[0]) for d in data)
#         elif type in convert:
#             return convert[type](data)
#         return data

# list1 = [0, 1, "s", "ii"]
# list2 = [1, 2, 3.14, 4]
# list3 = [list2 for _ in range(4)]
# res = convert_to_type(list3, List[List[Union[str, int]]])
# for arr in res:
#     for elem in arr:
#         print(f"VALUE: {elem}, TYPE: {type(elem)}")

def test():
    return

print(type(test))

print(type(str), type(list), type(int), type(lambda x: str(x)))