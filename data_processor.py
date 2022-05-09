from utils import load_pkl


class DataProcessor:
    def __init__(
        self,
        config,
    ):
        self.config = config
        self.label_map = load_pkl(f"{self.config.restore_path}/label_map.pkl")
        self.label_count = load_pkl(f"{self.config.restore_path}/label_count.pkl")
        self.label_map_rev = {i: k for k, i in self.label_map.items()}