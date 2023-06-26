from typing import Optional, List


def get_output_schema(
    output_type: str,
    possible_values: Optional[List] = None
):
    return {
        "reasoning": "Concise description of the reasoning behind the decision",
        "final_decision_value": {
            "description": "the actual decision value, may be null if no decision was possible",
            "type": output_type,
            **({"enum": possible_values} if possible_values is not None else {})
        }
    }
