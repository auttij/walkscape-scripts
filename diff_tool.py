from file_utils import read_json, write_json, json_files, get_localization
from jsondiff import diff
import filecmp
from os.path import exists

class DiffTool:
  def __init__(self, included_keys=None, excluded_keys=None) -> None:
    self.included = included_keys if  included_keys else []
    self.excluded = excluded_keys if excluded_keys else []
    self.diff = {}

  def create_diff_structure(self, src_1, src_2):
    def trim_filename(filename):
      return filename.split('/')[-1].split('\\')[-1].split('.')[0]
    
    relatative_files_1 = json_files(src_1, True)
    relatative_files_2 = json_files(src_2, True)
    in_both = [trim_filename(i) for i in relatative_files_1 if i in relatative_files_2]

    absolute_files_1 = json_files(src_1)
    absolute_files_2 = json_files(src_2)

    def list_find(l, subs):
      return [i for i in l if subs in i][0]

    return {
      e: { 'path_1': list_find(absolute_files_1, e), 'path_2': list_find(absolute_files_2, e) } for e in in_both
    }

  def base_diff_from_src(self, src_1, src_2, filename=None):
    diff_strucutre = self.create_diff_structure(src_1, src_2)
    base_diff = self.generate_diffs(diff_strucutre)
    if filename:
      write_json(filename, base_diff)
    return base_diff

  def base_diff_from_file(self, filename):
    return read_json(filename)

  def create_diff(self, src_1, src_2, filename=None):
    if filename and exists(filename):
      print(f'loading diff from file: {filename}')
      base_diff = self.base_diff_from_file(filename)
    else:
      print('generating diff from source')
      base_diff = self.base_diff_from_src(src_1, src_2, filename)

  def generate_diffs(self, base_diff):
    for key, data in base_diff.items():
      base_diff[key]['diff'] = self.file_diff(key, data)
    print(base_diff)
    return base_diff

  def file_diff(self, key, obj):
    print(f'generating diff for: {key}')
    path_1 = obj['path_1']
    path_2 = obj['path_2']

    if filecmp.cmp(path_1, path_2, shallow=False):
      print('no changes in file')
      return {}

    data_1 = read_json(path_1)
    data_2 = read_json(path_2)

    base_diff = diff(data_1, data_2, syntax='symmetric', marshal=True)
    return base_diff


  # def populate_diff(self):
  #   flat_diff = { k: v for k, v in base_diff.items() if str(k).isdigit() }
  #   for k in flat_diff:
  #     flat_diff[k]['action'] = 'update'

  #   others = [k for k in base_diff.keys() if not str(k).isdigit()]
  #   for diff_key in others:
  #     new_dict = { k: v for k, v in base_diff[diff_key] }
  #     for k in new_dict:
  #       new_dict[k]['action'] = str(diff_key)
  #     flat_diff = flat_diff | new_dict


  #   def name(key):
  #     try:
  #       return get_localization(key)
  #     except:
  #       return key

  #   named_diff = { name(data_2[k]['name']): v for k, v in flat_diff.items() }

  #   self.diff[key]['diff'] = named_diff



  def pretty_print(self):
    print()
    for category in self.diff:
      diff = self.diff[category]['diff']
      if diff:
        print(f"====== {category.capitalize()} ======\n")
        for name in diff:
          self.print_diff(name, diff[name], category)

  def print_diff(self, name, data, category):
    action = data['action']
    del data['action']

    if action == '$insert':
      print(f'added {name}')
    elif action == '$delete':
      print(f'removed {name}')
    else:    
      print(name)
      for key, value in data.items():
        self.human_readable_diff(key, value, action, category)
    print()

  def human_readable_diff(self, key, value, action, category):
    def inc_dec(v1, v2): return "decrease" if v1 > v2 else "increase"
    def value_inc_dec(v1, v2, text): return f"{inc_dec(v1, v2)} {text}: {v1} -> {v2}"
    def value_change(v1, v2, text): return f"{text}: {v1} -> {v2}"

    if key == 'xpRewardsMap':
      for skill, xp_diff in value.items():
        print(value_inc_dec(xp_diff[0], xp_diff[1], f"{skill} xp"))

    elif key == 'parallax':
      print('change background parallax')

    elif key == 'workRequired':
      print(value_inc_dec(value[0], value[1], "work required"))

    elif key == 'maxWorkEfficiency':
      print(value_inc_dec(value[0], value[1], "max work efficiency"))

    elif key == 'requirements':
      try:
        reqs = value[0]['requirements']
        for inner_obj in reqs.values():
          req = inner_obj['requirement']
          for inner_key, inner_value in req.items():
            print(value_change(inner_value[0], inner_value[1], f"changed {inner_key} requirement"))
      except KeyError:
        print(f'failed to find key for {value}')

    elif key == 'rewards':
      try:
        rews = value[0]['rewards']
        for inner_obj in rews.values():
          rew = inner_obj['reward']
          for inner_key, inner_value in rew.items():
            print(value_change(inner_value[0], inner_value[1], f"changed {inner_key} reward"))
      except KeyError:
        print(f'failed to find key for {value}')

    elif key == 'keywords':
      print(value)
      for inner_key, inner_values in value.items():
        for inner_value in inner_values:
          print(f"{inner_key} keyword {inner_value}")

    elif key == 'materials':
      print('changed materials')

    elif key == 'tableRows':
      for inner_key, inner_values in value.items():
        if 'insert' in str(inner_key) or 'delete' in str(inner_key):
          for _, inner_value in inner_values:
            print(f'{str(inner_key)} item: {inner_value["rowItemID"]}')
        else:
          for ik, iv in inner_values.items():
            print(value_change(iv[0], iv[1], f"{ik} changed"))

    elif key in ['difficulty', 'path', 'activityIcon', 'itemIcon', 'locationDynamicBackgroundPath']:
      print(value_change(value[0], value[1], f'changed {key}'))

    elif key in ['shownMaterials', 'cardBackImage']:
      pass

    else:
      print(key, value)

def main():
  path_0 = "C:\\Games\\Walkscape\\data files\\0.2.0-beta+322"
  path_1 = "C:\\Games\\Walkscape\\data files\\0.2.0-beta+323"
  path_2 = "C:\\Games\\Walkscape\\data files\\0.2.0-beta+324"
  excluded = [] #['parallaxes', 'pfp_options', 'items', 'achievements', 'activities', 'locations', 'attributes', 'buildings', 'characters', 'default_unlocks', 'factions', 'game_data', 'items', 'job_boards', 'banned_keywords', 'keywords', 'loot_tables', 'pfp_option_groups', 'reward_progress', 'routes', 'services', 'shops', 'stats', 'terrain_modifiers']


  d = DiffTool()
  d.base_diff_from_src(path_0, path_1, "323_diff.json")
  # d.pretty_print()

if __name__ == '__main__':
  main()