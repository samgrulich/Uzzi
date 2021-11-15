"Group of unique functions, works across all nft pages"

import os
import json


class DataLoader:
    @staticmethod
    def Save(data: object, path: str) -> None:
        "Save your object to file"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data.__dict__, f, ensure_ascii=False, indent=4)

    @staticmethod
    def Load(path: str, out_obj: object) -> object:
        """
        Load object form file
        \t returns None if action was unsuccessful 
        """
        if not os.path.exists(path):
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return out_obj.__dict__.update(json.load(f))
