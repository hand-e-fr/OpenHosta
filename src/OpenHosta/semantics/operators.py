from ..exec.closure import closure, closure_async

def test(
    test_string:str="return False",
    *args,
    **kwargs
    ) -> bool:
    return closure(query_string=test_string, force_return_type=bool)(*args, **kwargs)

async def test_async(test_string:str, *args, **kwargs) -> bool:
    return await closure_async(test_string, force_return_type=bool)(*args, **kwargs)