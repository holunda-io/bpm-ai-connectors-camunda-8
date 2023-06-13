import json
import requests
import yaml


def resolve_ref(obj, data):
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref_path = obj["$ref"].split("/")[1:]
            target = data
            for path in ref_path:
                target = target.get(path, {})
            return resolve_ref(target, data)
        else:
            return {k: resolve_ref(v, data) for k, v in obj.items() if k not in ["security"]}
    elif isinstance(obj, list):
        return [resolve_ref(i, data) for i in obj]
    else:
        return obj


def extract_routes(data):
    paths = data.get('paths', {})
    tags = {tag['name']: tag['description'] for tag in data.get('tags', [])}
    result = []

    for route, route_def in paths.items():
        route_def_resolved = resolve_ref(route_def, data)
        for method, details in route_def_resolved.items():
            tags_for_route = details.get('tags', [])
            result.append({
                "route": route,
                "method": method,
                "definition": details,
                "tags": [(tag, tags.get(tag, '')) for tag in tags_for_route]
            })

    return result


def json_to_yaml(json_str):
    data = json.loads(json_str)
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def generate_operation_strings(routes):
    operation_strings = []
    current_tags = set()

    for route in routes:
        for tag, description in route['tags']:
            if tag not in current_tags:
                operation_strings.append(f"\n# {tag}: {description}")
                current_tags.add(tag)
        operationId = route["definition"].get('operationId', '')
        summary = route["definition"].get('summary', '')
        operation_strings.append(f"- {operationId} ({route['method'].upper()}): {summary}")

    return operation_strings


def remove_tags_field(routes):
    for route in routes:
        if "tags" in route:
            del route["tags"]
        if "tags" in route["definition"]:
            del route["definition"]["tags"]
    return routes


def get_route_by_operation_id(routes, operation_id):
    for route in routes:
        if route['definition']['operationId'] == operation_id:
            return route
    return None



# data = requests.get('https://petstore.swagger.io/v2/swagger.json').json()
# routes = extract_routes(data)
# #
# routes = remove_tags_field(routes)
# #
# # print(json_to_yaml(json.dumps(routes)))
# #print("\n".join(generate_operation_strings(routes)))
# print(json_to_yaml(json.dumps(get_route_by_operation_id(routes, "addPet"))))
