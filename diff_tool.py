from file_utils import read_json, write_json, json_files, get_localization
from jsondiff import diff
import filecmp
from os.path import exists
import json
import sys


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

    def pretty_print_2(self, output_filename=None):
        fname = output_filename if output_filename else sys.stdout
        with open(fname, "w") as file:
            for category in self.diff:
                print(f"====== {category.capitalize()} ======\n", file=file)
                diff = self.diff[category]
                for key in diff:
                    change = diff[key]
                    action = change["action"]
                    del change["action"]

                    if action != "update" or key in ["$insert", "$delete"]:
                        name_keys = ["name", "id", "type"]
                        found = [
                            self.get_name(change[i]) for i in name_keys if i in change
                        ]
                        new_key = found[0] if len(found) else key
                        action_word = "added" if "insert" in action else "removed"
                        print(action_word, new_key, file=file)
                    else:
                        print(key.capitalize(), file=file)
                        output = self.process_diff(change, [])
                        for line in output:
                            print(line, file=file)
                        print(file=file)
                print(file=file)

    def process_diff(self, diff, path=None):
        result = []

        def get_descriptive_text(obj):
            if "type" in obj:
                if obj["type"] == "item" and "item" in obj:
                    obj = json.loads(obj["item"])
                elif obj["type"] == "pfpOption":
                    obj = {"item": "pfpOption"}

            changed_keys = [
                i for i in obj.keys() if i not in ["name", "desc", "id", "type"]
            ]
            if not len(changed_keys):
                changed_keys = [
                    i for i in obj.keys() if i in ["name", "desc", "id", "type"]
                ]
            changed_key = changed_keys[0]
            return f"{changed_key} {obj[changed_key]}"

        def build_text(path, text_path, value):
            if len(value) == 2:
                old_value, new_value = value
                if isinstance(new_value, dict):
                    new_value = get_descriptive_text(new_value)
                if isinstance(old_value, int) and not isinstance(new_value, int):
                    if "$insert" in path:
                        text = f"{text_path} added {new_value}"
                    elif "$delete" in path:
                        text = f"{text_path} removed {new_value}"
                elif old_value and not new_value:
                    text = f"{text_path} removed {old_value}"
                elif not old_value and new_value:
                    text = f"{text_path} added {new_value}"
                else:
                    text = f"{text_path} changed from {old_value} to {new_value}"
            else:
                print("weird value length", value)
            return text

        for key, value in diff.items():
            display_key = (
                "" if "reroll-this" in key or key.isdigit() or key == "" else key
            )
            if display_key and display_key not in path:
                path.append(display_key)
            filter_words = ["$delete", "$insert"]
            filtered_path = [i for i in path if i not in filter_words]
            new_path = "->".join(filtered_path)

            if (
                isinstance(value, list)
                and len(value) == 2
                and not isinstance(value[0], list)
            ):
                text = build_text(path, new_path, value)
                result.append(text)

            elif isinstance(value, dict):
                result += self.process_diff(value, path)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, dict):
                        result += self.process_diff(v, path)
                    elif isinstance(v, list) and len(v) == 2:
                        text = build_text(path, new_path, v)
                        result.append(text)

        return result


def main():
    path_0 = "C:\\git\\personal\\walkscape-scripts\\data\\data files\\0.2.0-beta+322"
    path_1 = "C:\\git\\personal\\walkscape-scripts\\data\\data files\\0.2.0-beta+323"
    path_2 = "C:\\git\\personal\\walkscape-scripts\\data\\data files\\0.2.0-beta+324"
    excluded = (
        []
    )  # ['parallaxes', 'pfp_options', 'items', 'achievements', 'activities', 'locations', 'attributes', 'buildings', 'characters', 'default_unlocks', 'factions', 'game_data', 'items', 'job_boards', 'banned_keywords', 'keywords', 'loot_tables', 'pfp_option_groups', 'reward_progress', 'routes', 'services', 'shops', 'stats', 'terrain_modifiers']

    d = DiffTool()
    d.create_diff(path_0, path_1, "323_diff.json")
    d.pretty_print_2(output_filename="changelog.txt")


if __name__ == "__main__":
    main()
