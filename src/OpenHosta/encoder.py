from typing import Any

class HostaEncoder():
    def __init__(self) -> None:
        None

    def encode(self, value: Any):
        if type(value) == int:
            return IntEncoder.encoder(value)
        elif type(value) == float:
            return FloatEncoder.encoder(value)
        # elif type(value) == bool:
        #     return BoolEncoder.encoder(value)
        elif type(value) == str:
            try:
                convert_type = FloatEncoder.encoder(value)
                return convert_type
            except:
                # return StringEncoder.encoder(value)
                None
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




class BoolEncoder(HostaEncoder):
    def __init__(self) -> None:
        super().__init__()

    def encoder(data):
        pass
        # data_encode = torch.zeros(len(data) * 2, dtype=torch.float16)

        # for i in range(len(data)):
        #     if data[i] == True:
        #         data_encode[i* 2] = torch.tensor(1, dtype=torch.float16)
        #     elif data[i] == False:
        #         data_encode[i* 2 + 1] = torch.tensor(1, dtype=torch.float16)

        # return data_encode, len(data_encode)


class StringEncoder(HostaEncoder):
    def __init__(self, data) -> None:
        super().__init__()
        self.data = data

    def encoder(data):
        pass
        # max_length = 32
        # data_ascii_tab = []
        # data_encode = []

        # for id in range(len(data)):    
        #     if len(data[id]) > max_length:
        #         raise ValueError("Data size is too long, expected {max_length} maximum")

        #     ascii_values = [ord(char) - 31 for char in data[id]]
        #     ascii_values += [0] * (max_length - len(ascii_values))
        #     data_ascii_tab.append(ascii_values)

        # data_encode = torch.tensor(data_ascii_tab, dtype=torch.float16)

        # return data_encode, len(data_encode)

