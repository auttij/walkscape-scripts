import json
import yaml
from functools import lru_cache
from os.path import exists

def read_json(filepath):
  with open(filepath, 'r') as jf:
    return json.load(jf)
    
def write_json(filepath, data):
  with open(filepath, 'w') as jf:
    json.dump(data, jf, ensure_ascii=False, indent=2)

@lru_cache
def read_yaml(filename):
  with open(filename, 'r') as file:
    return yaml.safe_load(file)

def get_localization(key):
  parts = key.split('.')
  localization_file = f"data/{parts[0]}_en-US.yaml"
  if not exists(localization_file):
    return key

  data = read_yaml(localization_file)
  for key in parts[1:]:
    data = data[key]
  return data

def get_named_data(filename):
  filename = f'data/{filename}'
  assert exists(filename)
  data = read_json(filename)
  return { get_localization(activity["name"]): activity for activity in data }

def main():
  pass

if __name__ == "__main__":
  main()