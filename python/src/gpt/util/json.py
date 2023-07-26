import json


def json_to_md(json_dict, depth=1):
    md_str = ""
    for key, value in json_dict.items():
        md_str += '#' * depth + ' ' + str(key) + '\n'
        if isinstance(value, dict):
            md_str += json_to_md(value, depth + 1)
        else:
            md_str += str(value) + '\n'
    return md_str

def write_json_to_file(dict_obj, filename):
    try:
        with open(filename, 'w') as file:
            file.write(json.dumps(dict_obj, indent=4))
        print(f"Dictionary successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
