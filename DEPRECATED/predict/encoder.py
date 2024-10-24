from typing import Any

class HostaEncoder():
    def __init__(self) -> None:
        None

    def encode(self, value: Any):
        if type(value) == int:
            return IntEncoder.encoder(value)
        elif type(value) == float:
            return FloatEncoder.encoder(value)
        elif type(value) == str:
            try:
                convert_type = FloatEncoder.encoder(value)
                return convert_type
            except:
                raise ValueError("String cannot be converted to float (numbers in string only supported for now)")
        else:
            raise ValueError("Type not supported")


class IntEncoder(HostaEncoder):
    def __init__(self) -> None:
        super().__init__()

    def encoder(data):
        data_encode = int(data)
        return [data_encode]

class FloatEncoder(HostaEncoder):
    def __init__(self) -> None:
        super().__init__()

    def encoder(data):
        data_encode = float(data)
        return [data_encode]
