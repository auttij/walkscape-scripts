from math import ceil
from file_utils import get_named_data

def activity_data():
  return get_named_data('activities.json')

def recipes_data():
  return get_named_data('recipes.json')

def pretty_print(title, groups):
  all_keys = [inner_list[0] for sub_list in groups.values() for inner_list in sub_list if inner_list]
  longest = max(list(map(len, all_keys)))
  
  print(f"\n{title:>{longest+10}}")
  for name, group in groups.items():
    print(f"\n{name.upper():>{longest+5}} ({len(group)})")
    for a, b in group:
      print(f"{a:>{longest}} - {b}")

def activity_work_efficiencies():
  data = activity_data()
  parsed = {}

  for name, activity in data.items():
    skill_key = [i for i in activity.keys() if i.startswith('relatedSkills')][0]
    skill = activity[skill_key][0]
    w_e = activity["maxWorkEfficiency"]
    if skill not in parsed:
        parsed[skill] = []
    parsed[skill].append([name, w_e])
  for skill, activities in parsed.items():
    s = sorted(activities, key=lambda x: x[1])
    parsed[skill] = [[x, f"{(w_e-1)*100:.0f}%"] for x, w_e in s]
  pretty_print("Max work efficiencies:", parsed)

def activity_min_steps():
  data = activity_data()
  parsed = {}

  for name, activity in data.items():
    skill_key = [i for i in activity.keys() if i.startswith('relatedSkills')][0]
    skill = activity[skill_key][0]
    work = activity["workRequired"]
    w_e = activity["maxWorkEfficiency"]
    min_steps = ceil(work/w_e)
    if skill not in parsed:
      parsed[skill] = []
    parsed[skill].append([name, min_steps])
  for skill, activities in parsed.items():
    parsed[skill] = sorted(activities, key=lambda x: x[1])
  pretty_print("Min steps:", parsed)

def effective_max_work_efficiencies():
  data = activity_data()
  parsed = {}

  for name, activity in data.items():
    skill_key = [i for i in activity.keys() if i.startswith('relatedSkills')][0]
    skill = activity[skill_key][0]
    
    work = activity["workRequired"]
    w_e = activity["maxWorkEfficiency"]
    min_steps = ceil(work/w_e)

    real_max_we = w_e
    while ceil(work/real_max_we) == min_steps:
      real_max_we -= 0.01

    ewe = round(real_max_we + 0.01, 2)
    if ewe != w_e:
      if skill not in parsed:
        parsed[skill] = []
      parsed[skill].append([name, w_e, ewe])
    
  for skill, activities in parsed.items():
    s = sorted(activities, key=lambda x: x[1])
    parsed[skill] = [[x, f"{(ewe-1)*100:.0f}% / {(w_e-1)*100:.0f}%"] for x, w_e, ewe in s]
  
  pretty_print("effictive max work efficiencies:", parsed)
    
def main():
  activity_work_efficiencies()
  # activity_min_steps()
  # effective_max_work_efficiencies()

if __name__ == "__main__":
  main()