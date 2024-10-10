import json
import yaml
from functools import lru_cache
from os.path import exists, join, relpath
from os import walk


def read_json(filepath):
    with open(filepath, "r") as jf:
        return json.load(jf)


def write_json(filepath, data):
    with open(filepath, "w") as jf:
        json.dump(data, jf, ensure_ascii=False, indent=2)


@lru_cache
def read_yaml(filename):
    with open(filename, "r") as file:
        return yaml.safe_load(file)


def get_localization(key):
    parts = key.split(".")
    localization_file = f"data/{parts[0]}.yaml"
    if not exists(localization_file):
        return key

    data = read_yaml(localization_file)
    for key in parts[1:]:
        data = data[key]
    return data


def get_named_data(filename):
    filename = f"data/{filename}"
    assert exists(filename)
    data = read_json(filename)
    return {get_localization(activity["name"]): activity for activity in data}


def files_by_type(src, file_type, relative_path=False):
    for root, dirs, files in walk(src):
        for file in files:
            if file.endswith(file_type):
                if relative_path:
                    rel_dir = relpath(root, src)
                    yield (join(rel_dir, file))
                else:
                    yield (join(root, file))


def json_files(src, relative_path=False):
    return [i for i in files_by_type(src, ".json", relative_path)]


def main():
    pass


if __name__ == "__main__":
    main()
