import os
import json
from typing import Generic, TypeVar, Optional

T = TypeVar('T')
CACHE_PATH = "__hostacache__"

class HostaCache(Generic[T]):
    def __init__(self, hash_key: str, data: T, verbose: bool = False):
        self.hash_key = hash_key
        self.data = data
        self.verbose = verbose
        self.folder_path = os.path.join(CACHE_PATH, self.hash_key)
        self.file_path = os.path.join(self.folder_path, "data.json")

        if not os.path.exists(CACHE_PATH):
            if self.verbose:
                print(f"Creating cache directory at {CACHE_PATH}")
            os.makedirs(CACHE_PATH)

        if not os.path.exists(self.folder_path):
            if self.verbose:
                print(f"Creating cache directory at {self.folder_path}")
            os.makedirs(self.folder_path)

        if not os.path.exists(self.file_path):
            if self.verbose:
                print(f"Creating cache file at {self.file_path}")
            self.save(data)
        else:
            if self.verbose:
                print(f"Loading data from cache file at {self.file_path}")
            loaded_data = self.load()
            if loaded_data != data:
                if self.verbose:
                    print(f"Data mismatch, updating cache file at {self.file_path}")
                self.save(data)

    def get(self) -> Optional[T]:
        return self.load()

    def save(self, data: T):
        with open(self.file_path, 'w') as file:
            json.dump(data.__dict__, file)
        if self.verbose:
            print(f"Data saved to cache file at {self.file_path}")

    def load(self) -> Optional[T]:
        if not os.path.exists(self.file_path):
            return None
        with open(self.file_path, 'r') as file:
            data_dict = json.load(file)
        return self.data_class(**data_dict)

    @property
    def data_class(self):
        raise NotImplementedError("Must be implemented in subclass")
