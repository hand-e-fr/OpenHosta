import os
import json
from typing import Generic, TypeVar, Optional

T = TypeVar('T')
CACHE_PATH = "__hostacache__"
PREFIX = "\033[0m\033[32m\033[1mHostaCache | \033[0m"

class HostaCache(Generic[T]):
    def __init__(self, hash_key: str, data: T, verbose: bool = False):
        self._hash_key = hash_key
        self._data = data
        self._verbose = verbose
        self._folder_path = os.path.join(os.getcwd(), CACHE_PATH, self._hash_key)
        self._file_path = os.path.join(self._folder_path, "data.json")

        if not os.path.exists(self._folder_path):
            if self._verbose:
                print(f"{PREFIX}Creating cache directory at {self._folder_path}")
            os.makedirs(self._folder_path)

        if not os.path.exists(self._file_path):
            if self._verbose:
                print(f"{PREFIX}Creating cache file at {self._file_path}")
            self.save(data)
        else:
            if self._verbose:
                print(f"{PREFIX}Loading data from cache file at {self._file_path}")
            loaded_data = self.load()
            if loaded_data != data:
                if self._verbose:
                    print(f"{PREFIX}Data mismatch, updating cache file at {self._file_path}")
                self.save(data)

    def get(self) -> Optional[T]:
        return self.load()

    def folder_path(self) -> str:
        return self._folder_path

    def file_path(self) -> str:
        return self._file_path

    def save(self, data: T):
        with open(self._file_path, 'w') as file:
            json.dump(data.__dict__, file)
        if self._verbose:
            print(f"{PREFIX}Data saved to cache file at {self._file_path}")

    def load(self) -> Optional[T]:
        if not os.path.exists(self._file_path):
            return None
        with open(self._file_path, 'r') as file:
            data_dict = json.load(file)
        return self.data_class(**data_dict)

    @property
    def data_class(self):
        raise NotImplementedError("Must be implemented in subclass")
