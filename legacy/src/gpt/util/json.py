import json


def json_to_md(json_obj, depth=2):
    markdown = ""
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                # If it's a list of objects, pretty print the JSON representation
                markdown += f"{'#' * depth} {key}\n\n```json\n{json.dumps(value, indent=2)}\n```\n\n"
            elif isinstance(value, (dict, list)):
                markdown += f"{'#' * depth} {key}\n"
                markdown += json_to_md(value, depth + 1)
            else:
                markdown += f"{key}: {value}\n"
        markdown += "\n"  # One newline at the end of an object
    elif isinstance(json_obj, list):
        for item in json_obj:
            if isinstance(item, (dict, list)):
                markdown += json_to_md(item, depth)
            else:
                markdown += f"- {item}\n"
        markdown += "\n"  # One newline at the end of a list
    else:
        markdown += f"{json_obj}\n\n"  # If any other type, print it with a newline
    return markdown


def write_json_to_file(dict_obj, filename):
    try:
        with open(filename, 'w') as file:
            file.write(json.dumps(dict_obj, indent=4))
        print(f"Dictionary successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
