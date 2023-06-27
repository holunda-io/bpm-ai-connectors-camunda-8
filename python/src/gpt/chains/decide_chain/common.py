from typing import Optional, List


def get_decision_output_schema(
    output_type: str,
    possible_values: Optional[List] = None
):
    return {
        "reasoning": "concise description of the reasoning behind the decision",
        "decision": {
            "description": "the final decision value, may be null if no decision was possible",
            "type": output_type,
            **({"enum": possible_values} if possible_values is not None else {})
        }
    }
