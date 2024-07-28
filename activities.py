from math import ceil
import file_utils

def get_named_data():
  filename = 'data/activities.json' 
  data = file_utils.read_json(filename)
  return { file_utils.get_localization(activity["name"]): activity for activity in data }

def pretty_print(title, groups):

  all_keys = [inner_list[0] for sub_list in groups.values() for inner_list in sub_list if inner_list]
  longest = max(list(map(len, all_keys)))
  
  print(f"\n{title:>{longest+10}}")
  for name, group in groups.items():
    l = sorted(group, key=lambda x: x[1])
    print(f"\n{name.upper():>{longest+5}} ({len(l)})")
    for a, b in l:
      print(f"{a:>{longest}} - {b}")

def activity_work_efficiencies():
  data = get_named_data()
  parsed = {}

  for name, activity in data.items():
    skill = [i for i in activity['levelRequirementsMap'].keys()][0]
    w_e = activity["maxWorkEfficiency"]
    if skill not in parsed:
        parsed[skill] = []
    parsed[skill].append([name, f"{(w_e-1)*100:.0f}%"])
  pretty_print("Max work efficiencies:", parsed)

def activity_min_steps():
  data = get_named_data()
  parsed = {}

  for name, activity in data.items():
    skill = [i for i in activity['levelRequirementsMap'].keys()][0]
    work = activity["workRequired"]
    w_e = activity["maxWorkEfficiency"]
    min_steps = ceil(work/w_e)
    if skill not in parsed:
      parsed[skill] = []
    parsed[skill].append([name, min_steps])
  pretty_print("Min steps:", parsed)
   


def main():
  activity_work_efficiencies()
  activity_min_steps()

if __name__ == "__main__":
  main()