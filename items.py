from math import ceil
import file_utils

def pretty_print(title, groups):
  all_keys = [inner_list[0] for sub_list in groups.values() for inner_list in sub_list if inner_list]
  longest = max(list(map(len, all_keys)))
  
  print(f"\n{title:>{longest+10}}")
  for name, group in groups.items():
    l = sorted(group, key=lambda x: x[1])
    print(f"\n{name.upper():>{longest+5}} ({len(l)})")
    for a, b in l:
      print(f"{a:>{longest}} - {b}")

def name(item):
  return file_utils.get_localization(item["name"])

def get_named_data():
  filename = 'data/items.json' 
  data = file_utils.read_json(filename)
  return { name(item): item for item in data }

def basicFilter(items, key, value):
  return { name: val for name, val in items if val[key] == value }

def crafted():
  return basicFilter(get_named_data().items(), "type", "crafted")

def loot():
  return basicFilter(get_named_data().items(), "type", "loot")

def gear():
  return { **loot(), **crafted() }


class itemFilter:
  def __init__(self, preset=None):
    self.items = get_named_data()
    if preset == "gear":
      self.items = { name: val for name, val in self.items.items() if val["type"] in ["crafted", "loot"] }

  def basicFilter(self, key, value):
    self.items = { name: val for name, val in self.items.items() if val[key] == value }

  def crafted(self):
    self.basicFilter("type", "crafted")

  def loot(self):
    self.basicFilter("type", "loot")

  def slot(self, itemSlot):
    assert itemSlot in ['head', 'tool', 'chest', 'hands', 'feet', 'legs', 'back', 'cape', 'ring', 'neck', 'primary', 'secondary']
    return self.basicFilter("gearType", itemSlot)

def test():
  IF = itemFilter("gear")
  IF.slot("head")
  data = IF.items
  
  for name, item in data.items():
    print(name)

  # types = {}
  # for name, item in data.items():
  #   itemType = item["gearType"]
  #   if itemType not in types:
  #     types[itemType] = 0
  #   types[itemType] += 1
  
  # print(types.keys())
  # for type, value in types.items():
  #   print(type, value)
  # parsed = {}

  # for name, activity in data.items():
  #   skill = [i for i in activity['levelRequirementsMap'].keys()][0]
  #   w_e = activity["maxWorkEfficiency"]
  #   if skill not in parsed:
  #       parsed[skill] = []
  #   parsed[skill].append([name, f"{(w_e-1)*100:.0f}%"])
  # pretty_print("Max work efficiencies:", parsed)

def main():
  test()

if __name__ == "__main__":
  main()