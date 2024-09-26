class HostaDecoder():
    def __init__(self) -> None:
        pass

class FloatDecoder(HostaDecoder):
    def __init__(self) -> None:
        super().__init__()

    def decoder(data):
        data_decode = [float(x) for x in data]

        return data_decode, len(data_decode)
    
class IntDecoder(HostaDecoder):
    def __init__(self) -> None:
        super().__init__()

    def decoder(data):
        data_decode = [int(x) for x in data]

        return data_decode, len(data_decode)

    
class BoolDecoder(HostaDecoder):
    def __init__(self) -> None:
        super().__init__()
    
    def decoder(data):
        data_decode = [len(data) // 2]

        for i in range(len(data) // 2):
            if data[i * 2] == 1:
                data_decode[i] = True
            elif data[i * 2 + 1] == 1:
                data_decode[i] = False

        return data_decode, len(data_decode) * 2


class StringDecoder(HostaDecoder):
    def __init__(self) -> None:
        super().__init__()

    def decoder(data):
        data_decode = []

        # Check if data is a list of strings
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            for s in data:
                # Decode each character by adding 31 to its ASCII value
                decoded_chars = [chr(int(char) + 31) for char in s if char != 0]
                decoded_string = ''.join(decoded_chars)
                data_decode.append(decoded_string)
        else:
            raise ValueError("Data format not supported for decoding.")

        return data_decode, len(data)

class MultiDecoder(HostaDecoder):
    pass

class SimpleDecoder(HostaDecoder):
    pass

