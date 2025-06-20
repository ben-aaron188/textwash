from importlib.resources import files


class Config:
    """
    Configuration for data paths, model and language.
    `files(__package__)` ensures that the paths point to the root 
    of the installed package.
    """

    def __init__(self, language: str):
        data_dir = files(__package__).joinpath("data")
        
        self.path_to_months_file = data_dir / "months.txt"
        self.path_to_written_numbers_file = data_dir / "written_numbers.txt"
        
        if language not in ("nl", "en"):
            raise ValueError("language must be 'nl' or 'en'")
        self.model_path = data_dir / language
        self.model_type = "bert" if language == "nl" else "roberta"
