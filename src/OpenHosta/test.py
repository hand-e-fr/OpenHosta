import matplotlib.pyplot as plt
import numpy as np
import time as t
import inspect

from OpenHosta import model_config, Models, pmac, emulate, thought

time_array = []
score_array = []


model_config(model=Models.BEST, api_key="sk-proj-T7o4z8S4q9fnBNTdSq4iT3BlbkFJ82uVDLRaIAkx1sjwyE5C")

@pmac
def reverse_str_ia(a:str)->str:
    """
    This function reverse a string
    """  
    return emulate()

print(reverse_str_ia("bonjour"))
reverse_str_ia.__suggest__(reverse_str_ia)
print(reverse_str_ia.advanced)

# def reverse_string(s):
#     return s[::-1]

# start = t.time()

# word = "Bonjour"
# result = reverse_str_ia(word)
# print(result)

# end = t.time()
# duration = end - start

# time_array.append(duration)

# if result == reverse_string(word):
#     score_array.append(True)
# else:
#     score_array.append(False)
    
# print(f"lambda direct: {thought("Assemble les mots d'un tableau")(["Bonjour", "je", "suis", "rouge"])}")


# x = thought("Est-ce un prénom masculin")
# print(f"Lamnda objet: {x("Emmanuel")}")

# @pmac
# def compute(a:int, b:int)->int:
#     """
#     This function mutlipies the two integers in parameter and add the first to the result
#     """
#     return emulate()

# print(compute(5, 6))

# compute.__suggest__(compute)
# compute.diagramm

# index = list(range(1, len(time_array) + 1))
# colors = ['b'] * len(time_array)

# for k in range(len(time_array)):
#     if score_array[k] == True:
#         colors[k] = 'b'
#     else:
#         colors[k] = 'r'

# average_time = np.mean(time_array)

# score = sum([1 if not x else 0 for x in score_array]) / len(score_array)

# plt.figure(figsize=(10, 5))
# plt.plot(index, time_array, linestyle='-', color='gray')

# plt.scatter(index, time_array, color=colors, s=200)

# plt.axhline(y=average_time, color='c', linestyle='--', label=f'Mean time: {average_time:.2f} s')
# plt.axhline(y=0, color='w', linestyle='--', label=f'Errors: {score:.2f}%')
# plt.axhline(y=0, color='w', linestyle='--', label=f'Nb: {len(score_array):.2f}')

# plt.title('Func: reverse a string')
# plt.xlabel('Index')
# plt.ylabel('Execution time (sec)')

# plt.grid(True)
# plt.legend()
# plt.show()

#################################################################################################################""

# def toto(a:int=0):
#     x = inspect.currentframe()
#     # print(x.f_locals.keys())
#     # print(x.f_locals.values())
#     # print(x.f_locals["a"])
#     func = x.f_back.f_locals[x.f_code.co_name]
#     print(func.__name__)

# toto()
# print(toto)