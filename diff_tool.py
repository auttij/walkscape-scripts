from file_utils import read_json, write_json, json_files, get_localization
from jsondiff import diff
import filecmp
from os.path import exists
import json


class DiffTool:
    def __init__(self, included_keys=None, excluded_keys=None) -> None:
        self.included = included_keys if included_keys else []
        self.excluded = excluded_keys if excluded_keys else []
        self.diff = {}

    def create_diff_structure(self, src_1, src_2):
        def trim_filename(filename):
            return filename.split("/")[-1].split("\\")[-1].split(".")[0]

        relatative_files_1 = json_files(src_1, True)
        relatative_files_2 = json_files(src_2, True)
        in_both = [
            trim_filename(i) for i in relatative_files_1 if i in relatative_files_2
        ]

        absolute_files_1 = json_files(src_1)
        absolute_files_2 = json_files(src_2)

        def list_find(l, subs):
            return [i for i in l if subs in i][0]

        return {
            e: {
                "path_1": list_find(absolute_files_1, e),
                "path_2": list_find(absolute_files_2, e),
            }
            for e in in_both
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
            print(f"loading diff from file: {filename}")
            base_diff = self.base_diff_from_file(filename)
        else:
            print("generating diff from source")
            base_diff = self.base_diff_from_src(src_1, src_2, filename)

        populated_diff = {}
        for category, data in base_diff.items():
            if data["diff"]:
                populated_diff[category] = self.populate_diff(category, data)

        self.diff = populated_diff
        # print(json.dumps(populated_diff, indent=4))

    def generate_diffs(self, base_diff):
        for key, data in base_diff.items():
            base_diff[key]["diff"] = self.file_diff(key, data)
        print(base_diff)
        return base_diff

    def file_diff(self, key, obj):
        print(f"generating diff for: {key}")
        path_1 = obj["path_1"]
        path_2 = obj["path_2"]

        if filecmp.cmp(path_1, path_2, shallow=False):
            print("no changes in file")
            return {}

        data_1 = read_json(path_1)
        data_2 = read_json(path_2)

        base_diff = diff(data_1, data_2, syntax="symmetric", marshal=True)
        return base_diff

    def get_name(self, key):
        try:
            return get_localization(key)
        except:
            return key

    def populate_diff(self, category, data):
        data_2 = read_json(data["path_2"])
        base_diff = data["diff"]

        def populate_rec(key, value, related_data):
            added_keys = ["name", "id", "type"]

            if isinstance(value, dict) or isinstance(value, list):
                if isinstance(related_data, dict):
                    found = [
                        self.get_name(related_data[i])
                        for i in added_keys
                        if i in related_data
                    ]
                    new_key = (
                        found[0]
                        if (
                            (isinstance(key, str) and key.isdigit())
                            or (isinstance(key, int))
                        )
                        and len(found)
                        else key
                    )
                else:
                    new_key = key

                inner_diff = {} if isinstance(value, dict) else []
                if isinstance(value, dict):
                    for inner_key, inner_value in value.items():
                        if inner_key in ["$insert", "$delete"]:
                            return inner_key, value
                        elif isinstance(inner_key, str) and inner_key.isdigit():
                            inner_data = related_data[int(inner_key)]
                        else:
                            inner_data = related_data[inner_key]
                        new_inner_key, new_inner_value = populate_rec(
                            inner_key, inner_value, inner_data
                        )

                        if isinstance(inner_diff, dict):
                            inner_diff[new_inner_key] = new_inner_value
                        else:
                            inner_diff.append(new_inner_value)
                    return new_key, inner_diff

                if isinstance(value, list):
                    if isinstance(key, str):
                        return key, value
                    return "", value
            else:
                return key, value

        populated_diff = {}

        def populate_wrapper(populated_diff, processable_data, action):
            for key, value in processable_data.items():
                if key in ["$insert", "$delete"]:
                    populate_wrapper(
                        populated_diff, dict(processable_data[key]), key[1:]
                    )
                    continue
                else:
                    if isinstance(key, str) and key.isdigit():
                        inner_data = data_2[int(key)]
                    else:
                        inner_data = data_2[key]
                    new_key, populated_value = populate_rec(key, value, inner_data)

                populated_value["action"] = action
                populated_diff[new_key] = populated_value

        populate_wrapper(populated_diff, base_diff, "update")
        return populated_diff

    def pretty_print(self):
        print()
        for category in self.diff:
            diff = self.diff[category]
            if diff:
                print(f"====== {category.capitalize()} ======\n")
                for name in diff:
                    self.print_diff(name, diff[name], category)

    def print_diff(self, name, data, category):
        # action = data["action"]
        # del data["action"]

        # if action == "$insert":
        #     print(f"added {name}")
        # elif action == "$delete":
        #     print(f"removed {name}")
        # else:
        print(name)
        for key, value in data.items():
            self.human_readable_diff(key, value, category)
        print()

    def human_readable_diff_old(self, key, value, action, category):
        def inc_dec(v1, v2):
            return "decrease" if v1 > v2 else "increase"

        def value_inc_dec(v1, v2, text):
            return f"{inc_dec(v1, v2)} {text}: {v1} -> {v2}"

        def value_change(v1, v2, text):
            return f"{text}: {v1} -> {v2}"

        if key == "xpRewardsMap":
            for skill, xp_diff in value.items():
                print(value_inc_dec(xp_diff[0], xp_diff[1], f"{skill} xp"))

        elif key == "parallax":
            print("change background parallax")

        elif key == "workRequired":
            print(value_inc_dec(value[0], value[1], "work required"))

        elif key == "maxWorkEfficiency":
            print(value_inc_dec(value[0], value[1], "max work efficiency"))

        elif key == "requirements":
            try:
                reqs = value[0]["requirements"]
                for inner_obj in reqs.values():
                    req = inner_obj["requirement"]
                    for inner_key, inner_value in req.items():
                        print(
                            value_change(
                                inner_value[0],
                                inner_value[1],
                                f"changed {inner_key} requirement",
                            )
                        )
            except KeyError:
                print(f"failed to find key for {value}")

        elif key == "rewards":
            try:
                rews = value[0]["rewards"]
                for inner_obj in rews.values():
                    rew = inner_obj["reward"]
                    for inner_key, inner_value in rew.items():
                        print(
                            value_change(
                                inner_value[0],
                                inner_value[1],
                                f"changed {inner_key} reward",
                            )
                        )
            except KeyError:
                print(f"failed to find key for {value}")

        elif key == "keywords":
            print(value)
            for inner_key, inner_values in value.items():
                for inner_value in inner_values:
                    print(f"{inner_key} keyword {inner_value}")

        elif key == "materials":
            print("changed materials")

        elif key == "tableRows":
            for inner_key, inner_values in value.items():
                if "insert" in str(inner_key) or "delete" in str(inner_key):
                    for _, inner_value in inner_values:
                        print(f'{str(inner_key)} item: {inner_value["rowItemID"]}')
                else:
                    for ik, iv in inner_values.items():
                        print(value_change(iv[0], iv[1], f"{ik} changed"))

        elif key in [
            "difficulty",
            "path",
            "activityIcon",
            "itemIcon",
            "locationDynamicBackgroundPath",
        ]:
            print(value_change(value[0], value[1], f"changed {key}"))

        elif key in ["shownMaterials", "cardBackImage"]:
            pass

        else:
            print(key, value)

    def pretty_print_2(self):
        print()
        for category in self.diff:
            print(f"====== {category.capitalize()} ======\n")
            diff = self.diff[category]
            for key in diff:
                change = diff[key]
                action = change["action"]
                del change["action"]

                if action != "update" or key in ["$insert", "$delete"]:
                    name_keys = ["name", "id", "type"]
                    found = [self.get_name(change[i]) for i in name_keys if i in change]
                    new_key = found[0] if len(found) else key
                    action_word = "added" if "insert" in action else "removed"
                    print(action_word, new_key)
                else:
                    print(key.capitalize())
                    for inner_key, inner_value in change.items():
                        self.human_readable_diff(inner_key, inner_value)
                    print()
            print()

    def human_readable_diff(self, key, value):
        def action_word(key):
            if "insert" in key:
                return "added"
            if "delete" in key:
                return "removed"
            return "changed"

        def change_action(action, key):
            if action in ["added", "removed"]:
                return action
            return action_word(key)

        def value_change(v1, v2, text):
            return f"{text}: {v1} -> {v2}"

        def value_add_remove(v1):
            return f"{v1}"

        def diff_rec(action, key, value, level):
            action = change_action(action, key)
            if key in ["$insert", "$delete"]:
                if isinstance(value, dict):
                    for inner_key, inner_value in value.items():
                        diff_rec(action, inner_key, inner_value, level + 2)
                else:
                    for inner_value in value:
                        diff_rec(action, "", inner_value, level + 2)
            elif isinstance(value, list):
                if len(value):
                    if value[0] in ["$insert", "$delete"]:
                        print("???", value)
                    elif len(value) == 2 and value[0] == "" and value[1] != "":
                        text = "added: " + value_add_remove(value[1])
                    elif len(value) == 2 and value[1] == "" and value[0] != "":
                        text = "removed: " + value_add_remove(value[1])
                    elif (
                        len(value) == 2
                        and isinstance(value[0], int)
                        and isinstance(value[1], int)
                    ):
                        text = value_change(value[0], value[1], key)
                    elif (
                        len(value) == 2
                        and isinstance(value[1], dict)
                        and (
                            isinstance(value[0], int)
                            or ((isinstance(value[0], str) and value[0].isdigit()))
                        )
                    ):
                        changed_key = [
                            i
                            for i in value[1].keys()
                            if i not in ["name", "desc", "id", "type"]
                        ][0]
                        text = f"added: {changed_key} {value[1][changed_key]}"
                    elif len(value) == 2 and (
                        isinstance(value[0], int)
                        or ((isinstance(value[0], str) and value[0].isdigit()))
                    ):
                        if action == "added":
                            text = f"{action} {value_add_remove(value[0])}"
                        else:
                            text = f"{action} {value_add_remove(value[1])}"
                    elif len(value) == 2:
                        text = value_change(value[0], value[1], key)
                    else:
                        print("unknown list type value", value)
                    print(" " * level + text)
                    pass
            elif isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    inner_action = change_action("changed", inner_key)
                    if (
                        action
                        in [
                            "added",
                            "removed",
                        ]
                        and not isinstance(inner_value, dict)
                        and not isinstance(inner_value, list)
                    ):
                        if action == "added":
                            text = f"{action} {value_add_remove(value[1])}"
                        else:
                            text = f"{action} {value_add_remove(value[0])}"
                        print(" " * level + text)
                    elif inner_action in ["added", "removed"]:
                        pass
                    elif isinstance(inner_value, list):
                        text = f"{inner_action} {inner_key}:"
                        print(" " * level + text)
                        pass
                    elif (
                        inner_key
                        and key
                        and not (
                            isinstance(inner_key, int)
                            or (isinstance(inner_key, str) and inner_key.isdigit())
                        )
                    ):
                        text = f"{inner_action} {inner_key}:"
                        print(" " * level + text)
                    elif inner_key and not (
                        isinstance(inner_key, int)
                        or (isinstance(inner_key, str) and inner_key.isdigit())
                    ):
                        text = f"{action} {inner_key}:"
                        print(" " * level + text)
                    elif not key:
                        # print("no key", key, inner_key)
                        pass
                    elif not inner_key:
                        text = f"{action} {key}:"
                        print(" " * level + text)
                    else:
                        # print("dict no print", value)
                        pass

                    # print(inner_key, inner_action, action)
                    diff_rec(action, inner_key, inner_value, level + 2)
            elif isinstance(value, str):
                # print("str value ???", value)
                return value

        # print(value)
        diff_rec("update", key, value, 0)


def main():
    path_0 = "C:\\git\\personal\\walkscape-scripts\\data\\data files\\0.2.0-beta+322"
    path_1 = "C:\\git\\personal\\walkscape-scripts\\data\\data files\\0.2.0-beta+323"
    path_2 = "C:\\git\\personal\\walkscape-scripts\\data\\data files\\0.2.0-beta+324"
    excluded = (
        []
    )  # ['parallaxes', 'pfp_options', 'items', 'achievements', 'activities', 'locations', 'attributes', 'buildings', 'characters', 'default_unlocks', 'factions', 'game_data', 'items', 'job_boards', 'banned_keywords', 'keywords', 'loot_tables', 'pfp_option_groups', 'reward_progress', 'routes', 'services', 'shops', 'stats', 'terrain_modifiers']

    d = DiffTool()
    d.create_diff(path_1, path_2, "324_diff.json")
    d.pretty_print_2()
    # d.pretty_print()


if __name__ == "__main__":
    main()
