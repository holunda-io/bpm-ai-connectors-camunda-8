
def get_decision_output_schema(
    output_type: str,
    possible_values: list | None = None
):
    return {
        "reasoning": "concise description of the reasoning behind the decision",
        "decision": {
            "description": "the final decision value, may be null if no decision was possible",
            "type": output_type,
            **({"enum": possible_values} if possible_values is not None else {})
        }
    }


def get_cot_decision_output_schema(
    output_type: str,
    possible_values: list | None = None
):
    return {
        "reasoning": {
            "type": "object",
            "properties": {
                "relevantFacts": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A discrete fact"
                    }
                },
                "deducedInformation": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "Additional information that can be deduced from the relevantFacts"
                    }
                },
                "reasoningSteps": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A discrete reasoning step. Do not perform multiple steps in one. Be very fine-grained and use discrete steps/items."
                    }
                },
                "finalReasoning": {
                    "type": "string",
                    "description": "Concise description of the final reasoning behind the decision"
                }
            }
        },
        "decision": {
            "description": "The final decision value, may be null if no decision was possible",
            "type": output_type,
            **({"enum": possible_values} if possible_values is not None else {})
        }
    }