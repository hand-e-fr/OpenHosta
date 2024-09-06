import pytest
import time as t
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from OpenHosta import emulate, config

config.set_default_apiKey("")


def timer_tests(func):
    def wrapper(*args, **kwargs):
        g_c = "\033[94m"
        n = "\033[0m"
        bold = "\033[1m"

        start = t.time()
        rv = func(*args, **kwargs)
        end = t.time()

        duration = end - start
        print(f"{g_c}{bold}Execution time of {func.__name__}: {duration:.2f}s{n}")
        return (rv, duration)

    return wrapper


@timer_tests
def emulate_1args_int(arg) -> int:
    """Docstring"""
    return emulate()


@timer_tests
def emulate_2args_int(arg1, arg2) -> int:
    """Docstring"""
    return emulate()


class TestEmulate:

    @pytest.mark.parametrize(
        "name, doc, int1, int2, expected",
        [
            (
                "multiply",
                "This function mutliplies two integers in parameters",
                2,
                3,
                6,
            ),
            (
                "add", 
                "This function adds two integers in parameters", 
                2, 
                3, 
                5
            ),
            (
                "multiply_float",
                "This function multiplies two floating-point numbers in parameter.",
                3.8,
                7.7,
                29.26,
            ),
            (
                "power",
                "This function calculates the power of a number given a base (first arg) and an exponent (second arg).",
                4,
                5,
                1024,
            ),
            (
                "sum_list",
                "This function adds an integers in parameter to all integers in a list in parameter",
                10,
                [1, 6, 7, 12, 0],
                [11, 16, 17, 22, 10],
            ),
            (
                "substract",
                "This function substracts two integers in parameters",
                2,
                3,
                -1,
            ),
            (
                "divide",
                "This function divides the first integers in parameter by the second",
                621,
                3,
                207,
            ),
        ],
    )
    def test_math_basicOperation(self, name, doc, int1, int2, expected):
        emulate_2args_int.__name__ = name
        emulate_2args_int.__doc__ = doc
        result, duration = emulate_2args_int(int1, int2)
        assert result == expected

    @pytest.mark.parametrize(
        "name, doc, int1, int2, expected",
        [
            (
                "factorial",
                "This function calculates the factorial of a non-negative integer in parameter",
                10,
                -1,
                3628800,
            ),
            (
                "common_divisor",
                "This function returns the greatest common divisor of two integers in parameter.",
                36,
                60,
                12,
            ),
            (
                "square_root",
                "This function computes the square root of a given non-negative number in parameter.",
                144,
                -1,
                12,
            ),
            (
                "is_prime",
                "This function determines if a given integer is a prime number. Return 0 if true and 1 if false",
                199,
                -1,
                0,
            ),
        ],
    )
    def test_math_mediumOperation(self, name, doc, int1, int2, expected):
        if int2 == -1:
            emulate_1args_int.__name__ = name
            emulate_1args_int.__doc__ = doc
            result, duration = emulate_1args_int(int1)
        else:
            emulate_2args_int.__name__ = name
            emulate_2args_int.__doc__ = doc
            result, duration = emulate_2args_int(int1, int2)
        assert result == expected


# high number
# negative
# hard division
# duration test
