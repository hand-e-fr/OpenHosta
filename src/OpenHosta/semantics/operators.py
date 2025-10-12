from ..exec.closure import closure, closure_async

def test(test_string:str="return False"):
    return closure(query_string=test_string, force_return_type=bool)()

async def test_async(test_string:str):
    return await closure_async(test_string, force_return_type=bool)()