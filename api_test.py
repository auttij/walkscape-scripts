import requests
import csv
import json
from math import ceil

base_url = "http://wsapi.duckdns.org"

LEADERBOARD = {
    "STEPS": "total_steps",
    "XP": "total_xp",
    "LEVEL": "total_level",
    "AGILITY": "agility",
    "CARPENTRY": "carpentry",
    "COOKING": "cooking",
    "CRAFTING": "crafting",
    "FISHING": "fishing",
    "FORAGING": "foraging",
    "MINING": "mining",
    "SMITHING": "smithing",
    "WOODCUTTING": "woodcutting"
}

def read_csv(filename, delim=';'):
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delim)
        data = [row for row in csv_reader]
    return data

def read_json(filepath):
  with open(filepath, 'r') as jf:
    return json.load(jf)
  
def write_json(filepath, data):
    with open(filepath, 'w') as jf:
        json.dump(data, jf, ensure_ascii=False)

def get_xp_table():
    data = read_csv("xp.csv")
    out = [{ "total": -1, "xp": -1 }]
    for line in data[1:]:
        _, total, xp = line
        out.append({ "total": int(total), "xp": int(xp) })
    xp_table = out
    return xp_table

def xp_to_lvl(xp):
    xp_table = get_xp_table()
    i = 2
    while xp_table[i]["total"] < xp:
        i += 1
        if i == 99:
            return i
    return i - 1

def query(api_url, count=1000):
    per_page = min(count, 1000)
    pages = ceil(count / per_page)

    out = []
    for page in range(pages):
        url = f"{api_url}?page={page+1}&per_page={per_page}"
        print(f"querying {url}")
        response = requests.get(url)
        out.append(response.json()["payload"])
    return out

def get_leaderboard(type, count=1000):
    assert type in LEADERBOARD.values()
    data = query(f"{base_url}/leaderboard/{type}", count)
    write_json(f"leaderboard_{type}_top_{count}", data)
    return data

def player_skill(stats_obj, use_max=True, no_lvl_1=False):
    no = ["total_level", "total_xp", "total_steps"]
    stats = { key: stats_obj[key] for key in stats_obj.keys() if key not in no}
    if no_lvl_1:
        stats = { key: stats[key] for key in stats.keys() if stats[key] > 0 }

    skill = min(stats, key=stats.get)
    if use_max:
        skill = max(stats, key=stats.get)
    xp = stats[skill]
    return skill, xp_to_lvl(xp), xp

def process_data(fn, count=100, used_data=None, filename=None):
    assert used_data is not None or filename is not None
    data = used_data
    if filename:
        data = read_json(filename)
    fn(data, count)

def lowest_level_lb(data, count):
    parsed = []
    for player in data:
        name = player["username"]
        stats = player["stats"]
        low, low_lvl, low_xp = player_skill(stats, use_max=False)
        parsed.append([name, low_lvl, low, low_xp])
    out = sorted(parsed, key=lambda x: x[3], reverse=True)
    for i, line in enumerate(out[:count], start=1):
        print(f"{i:>2}: {line[0]:>15} {line[1]}  {line[2]:>11}  ({line[3]:,} xp)")

def lowest_skill(data):
    parsed = {}
    for player in data:
        low, *_ = player_skill(player["stats"], use_max=False)
        if low not in parsed:
            parsed[low] = 0
        parsed[low] += 1
        
    print("\n lowest level skill:")
    for key, value in sorted(parsed.items(), key=lambda x: x[1], reverse=True):
        print(f"{key:>13} - {value}")

def highest_skill(data):
    parsed = {}
    for player in data:
        hi, *_ = player_skill(player["stats"])
        if hi not in parsed:
            parsed[hi] = 0
        parsed[hi] += 1

    print("\n  highest level skill:")
    for key, value in sorted(parsed.items(), key=lambda x: x[1], reverse=True):
        print(f"{key:>13} - {value}")

def no_xp_skills(data):
    parsed = {}
    for player in data:
        stats = player["stats"]
        no_xp = [key for key, value in stats.items() if value == 0 ]
        for skill in no_xp:
            if skill not in parsed:
                parsed[skill] = 0
            parsed[skill] += 1
    print("\n  skills with no xp:")
    for key, value in sorted(parsed.items(), key=lambda x: x[1], reverse=True):
        print(f"{key:>13} - {value}")

def main():
    # lowest_level_lb()
    process_data(lowest_level_lb, 50, filename="output.json")
    # lowest_skill()
    # highest_skill()
    # no_xp_skills()
    # print()
    # get_leaderboard(LEADERBOARD["LEVEL"])
    pass

if __name__ == "__main__":
    main()