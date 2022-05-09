class Config:
    restore_path = "./data"
    load_model_path = f"{restore_path}/model.pth"
    path_to_months_file = f"{restore_path}/months.txt"
    path_to_written_numbers_file = f"{restore_path}/written_numbers.txt"

    max_len = 384
    unk_token = "[UNK]"
    pad_token = "[PAD]"
