import os
from datetime import datetime

class PredictCache:
    _instance = None

    def __new__(cls, path: str = None):
        if cls._instance is None:
            cls._instance = super(PredictCache, cls).__new__(cls)
            if path is not None:
                cls._instance._initialize(path)
        return cls._instance

    def _initialize(self, path: str):
        self.weights_path = os.path.join(path, "weights.pth")
        self.architecture_path = os.path.join(path, "architecture.json")
        self.summary_path = os.path.join(path, "summary.txt")
        self.data_path = os.path.join(path, "data.npy")

        if not os.path.exists(path):
            os.makedirs(path)

        if not os.path.exists(self.architecture_path):
            with open(self.architecture_path, "w") as file:
                file.write("")

        if not os.path.exists(self.summary_path):
            with open(self.summary_path, "w") as file:
                file.write("=== Log Summary ===\n")

        if not os.path.exists(self.weights_path):
            with open(self.weights_path, "wb") as file:
                pass

        if not os.path.exists(self.data_path):
            with open(self.data_path, "wb") as file:
                pass

    def __init__(self, path: str = None):
        pass

    def log(self, message: str, level: str = "INFO"):
        with open(self.summary_path, "a") as file:
            file.write(f"[{datetime.now()}] [{level}] {message}\n")

    def update_architecture(self, architecture: str):
        with open(self.architecture_path, "w") as file:
            file.write(architecture)
