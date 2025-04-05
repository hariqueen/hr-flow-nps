import json

def load_business_data(json_path: str) -> list:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
