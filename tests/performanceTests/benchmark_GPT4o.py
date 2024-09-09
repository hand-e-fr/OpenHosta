node = {"name": "", "duration": -1, "score": True}
test_info = []

def add_to_benchmark(name:str, duration:float, score:bool):
    global node, test_info
    new = dict(node)
    new["name"], new["duration"], new["score"] = name, duration, score
    test_info.append(new)
    return test_info