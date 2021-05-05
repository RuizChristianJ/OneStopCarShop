import pytest
import json
import os
from src.scraper import get_make_id, SelectionEnum


def test_differences():
    makes = get_make_id(SelectionEnum.allMakes)
    filename = 'makes.json'
    folder_path = (os.path.dirname(os.path.dirname(__file__)))
    file = os.path.join(folder_path, filename)
    f = open(file)
    makes_json = json.load(f)

    make_keys = makes.keys()
    make_json_keys = makes_json.keys()
    for key in make_keys:
        assert key in make_json_keys, f'{key} missing in JSON file'
        assert makes[key] == makes_json[key], f'{key} value does not match JSON'

    f.close()
