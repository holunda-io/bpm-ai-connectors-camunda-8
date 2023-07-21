import json
import random
import re
import string
from typing import List


class Element:
    def __init__(self, element_info):
        self.type = element_info.get("type")
        self.name = element_info.get("name")
        self.instruction = element_info.get("instruction", "")
        self.input_variables = element_info.get("input_variables", [])
        self.output_variable = element_info.get("output_variable", "")
        self.output_schema = element_info.get("output_schema", {})

    def run(self, process_variables: dict):
        if self.input_variables:
            for i, match in [(i, re.match(r"(\w+)\.?(\w+)?", i)) for i in self.input_variables]:
                if not match:
                    raise Exception(f"Invalid input to element '{self.name}': '{i}'. Valid pattern is '(\w+)\.?(\w+)?'.")
                variable, field = match.groups()
                if variable not in process_variables.keys():
                    raise Exception(f"Error running element '{self.name}': Input variable '{variable}' not defined!")

                value = process_variables[variable]

                if field:
                    if not isinstance(value, dict):
                        raise Exception(f"Error running element '{self.name}': Variable '{variable}' is not an object and thus has no field '{field}'.")
                    if field not in value.keys():
                        raise Exception(f"Error running element '{self.name}': Field '{field}' not defined in '{variable}'.")

        output_value = None
        if self.type not in ["start", "end", "gateway"]:
            output_value = self.mock_task()

        if self.output_variable:
            return {self.output_variable: output_value}
        else:
            return {}

    def mock_task(self):
        output_value = {}
        if not self.output_variable:
            return
        for key, schema in self.output_schema.items():
            if schema["type"] == "string":
                output_value[key] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            elif schema["type"] == "boolean":
                output_value[key] = bool(random.getrandbits(1))
            elif schema["type"] == "number":
                output_value[key] = random.uniform(1, 100)
            elif schema["type"] == "object":
                output_value[key] = {"key1": "value1", "key2": "value2"}
            elif schema["type"] == "array":
                output_value[key] = [random.randint(1, 10) for _ in range(5)]
            elif schema["type"] == "null":
                output_value[key] = None
        return output_value


class Flow:
    def __init__(self, flow_info):
        self.start = flow_info.get("from")
        self.end = flow_info.get("to")
        self.condition = flow_info.get("condition", None)


class Engine:
    def __init__(self, element_infos: List[dict], flow_infos: List[dict]):
        self.elements = {element_info["name"]: Element(element_info) for element_info in element_infos}
        self.flows = [Flow(flow_info) for flow_info in flow_infos]
        self.log = []
        self.variables = {}

        self.raw_elements = []
        self.raw_flows = []

    def add_element(self, element_info):
        elem = Element(element_info)
        if elem.output_variable and not elem.output_schema:
            raise Exception("output_schema required if element has an output variable.")
        elif elem.output_schema:
            for t in elem.output_schema.values():
                if not isinstance(t, dict) or (not t.get("type", None) or not t.get("description", None)):
                    raise Exception('output_schema must be json schema of form: {"foo": {"type": "<type>", "description": "<description>"}, ...}')
        self.elements[elem.name] = elem
        self.raw_elements.append(element_info)

    def add_flow(self, flow_info):
        flow = Flow(flow_info)
        if flow.start == flow.end:
            raise Exception(f"Flow ('{flow.start}', '{flow.end}') creates direct loop")
        if flow.start not in self.elements.keys():
            raise Exception(f"Flow start element '{flow.start}' does not exist.")
        if flow.end not in self.elements.keys():
            raise Exception(f"Flow end element '{flow.end}' does not exist.")
        if not flow.condition or self.parse_condition(flow.condition):
            self.flows.append(flow)
            self.raw_flows.append(flow_info)

    def run(self, input_values):
        self.log.clear()

        self.variables = input_values

        start_element = [n for n in self.elements.values() if n.type == "start"]
        if not start_element:
            raise Exception("No start event found.")

        current_element = start_element[0]
        while current_element.type != "end":
            self.log.append(f"Running {current_element.name}")
            output_values = current_element.run(self.variables)
            self.update_variables(output_values)

            next_element_name = self.get_next_element(current_element.name)
            current_element = self.elements[next_element_name]

        self.log.append(f"End process at {current_element.name}")

    def update_variables(self, output_values):
        if not output_values:
            return
        for variable, value in output_values.items():
            if "." in variable:
                outer, inner = variable.split(".")
                if outer not in self.variables:
                    self.variables[outer] = {}
                self.variables[outer][inner] = value
            else:
                self.variables[variable] = value

    def get_next_element(self, current_element_name):
        has_outgoing_flow = False
        for flow in self.flows:
            if flow.start == flow.end:
                raise Exception(f"Error running element '{current_element_name}': Flow ('{flow.start}', '{flow.end}') creates direct loop")
            if flow.start == current_element_name:
                has_outgoing_flow = True
                if flow.condition is None or self.eval_condition(flow.condition):
                    return flow.end
        if has_outgoing_flow:
            raise Exception(f"Error running element '{current_element_name}': Could not activate any outgoing flow. Check conditions.")
        else:
            raise Exception(f"Error running element '{current_element_name}': No outgoing flow!")

    def eval_condition(self, condition: str):
        neg, variable, field = self.parse_condition(condition)

        if variable not in self.variables.keys():
            raise Exception(f"Invalid condition: '{condition}': Variable '{variable}' not found.")

        if field:
            var_value = self.variables[variable]
            if not isinstance(var_value, dict):
                raise Exception(f"Invalid condition: '{condition}': Variable '{variable}' is not an object and thus has no field '{field}'.")
            if field not in var_value.keys():
                raise Exception(f"Invalid condition: '{condition}': Field '{field}' not defined in '{variable}'.")
            value = self.variables[variable][field]
        else:
            value = self.variables[variable]

        if isinstance(value, dict):
            raise Exception(f"Invalid condition: '{condition}': Variable '{variable}' is an object but condition must evaluate to a boolean.")
        if not isinstance(value, bool):
            raise Exception(f"Invalid condition: '{condition}': Condition must evaluate to a boolean but instead evaluated to '{value}'.")

        if neg:
            value = "not " + str(value)

        return eval(str(value))

    @staticmethod
    def parse_condition(condition) -> tuple:
        matches = re.findall(r"(!)?(\w+)\.?(\w+)?", condition)
        if len(matches) > 1:
            raise Exception(f"Invalid condition: '{condition}'. Supported condition pattern is '(!)?(\w+)\.?(\w+)?'")
        if not matches:
            raise Exception(f"Invalid condition: '{condition}'. Supported condition pattern is '(!)?(\w+)\.?(\w+)?'")
        return matches[0]

# nodes_info = [
#     {
#         "type": "start",
#         "name": "Start"
#     },
#     {
#         "type": "customer_database_task",
#         "name": "Find customer id",
#         "instruction": "Find the id of the customer by his email",
#         "input_variables": ["customer_email"],
#         "output_variable": "id_result",
#         "output_schema": {"customer_id": {"type": "string", "description": "the id of the customer"}}
#     },
#     {
#         "type": "user_task",
#         "name": "Delete customer",
#         "instruction": "Delete the customer record",
#         "input_variables": ["id_result.customer_id"],
#         "output_variable": "delete_result",
#         "output_schema": {"success": {"type": "boolean", "description": "result"}}
#     },
#     {
#         "type": "gateway",
#         "name": "Customer deleted?"
#     },
#     {
#         "type": "end",
#         "name": "Customer deleted"
#     },
#     {
#         "type": "end",
#         "name": "Customer not deleted"
#     },
# ]
#
# edges_info = [
#     {
#         "from": "Start",
#         "to": "Find customer id"
#     },
#     {
#         "from": "Find customer id",
#         "to": "Delete customer"
#     },
#     {
#         "from": "Delete customer",
#         "to": "Customer deleted?"
#     },
#     {
#         "from": "Customer deleted?",
#         "to": "Customer deleted",
#         "condition": "delete_result.success"
#     },
#     {
#         "from": "Customer deleted?",
#         "to": "Customer not deleted",
#         "condition": "!delete_result.success"
#     }
# ]
#
# input_values = {
#     "customer_email": "test@test.com"
# }
#
# engine = Engine([], edges_info)
#
# for n in nodes_info:
#     engine.add_element(n)
#
# engine.run(input_values)
#
# print('\n'.join(engine.log))
# print('')
# print(json.dumps(engine.variables, indent=2))
