import json
import os

from typing import Any


class JSONDatabase(object):
    def __init__(self, file: str="data.json"):
        self.file = file
        self.data = {}
        self.load_data()
    

    def load_data(self):
        if not os.path.exists(self.file):
            return
        
        with open(self.file) as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            return
        
        self.data = data
    

    def get_data(self, keys: str | None=None) -> Any:
        current_data = self.data

        if keys is not None:
            for key in keys.split("."):
                if not isinstance(current_data, dict):
                    return None
                
                current_data = current_data.get(key)
        
        return current_data
