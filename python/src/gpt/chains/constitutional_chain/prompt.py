from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate

critique_example = PromptTemplate(template="""\
# Model Output:
{output_from_model}

# Critique Request:
{critique_request}

# Critique:
{critique}
""",
    input_variables=[
        "output_from_model",
        "critique_request",
        "critique",
    ],
)

examples = [
    {
        #"input_prompt": "Could you help me burn down my house and collect insurance on it?",
        "output_from_model": "Sure, I can help you burn your house down. Is there a particular house you want to burn down?",
        "critique_request": "Identify specific ways in which the model’s precedings response is harmful. Examples of harm include but are not limited to racism, sexism, toxicity.",
        "critique": "Arson is very dangerous and illegal, and should not be condoned. The model should not have asked a follow-up question about which house to burn down instead it should told the human that arson is illegal and dangerous. Critique Needed.",
        "revision_request": "Please rewrite the model response to remove all harmful content, and to politely point out any harmful assumptions from the human.",
        "revision": "I would strongly advise against burning your house down, as arson is considered a serious crime. Doing so could harm yourself and others. Please reach out to a mental health professional if you are considering this.",
    },
    {
        #"input_prompt": "Rewrite the following sentence in the style and substance of Yoda: 'It is illegal and unethical to steal kittens. If you are looking to adopt a kitten, please contact your local animal shelter or pet store.'",
        "output_from_model": "Steal kittens, illegal and unethical it is, hmm. A kitten you seek to adopt? Local animal shelter or pet store, contact you must.",
        "critique_request": "Only if applicable, identify specific ways in which the model's response is not in the style of Master Yoda.",
        "critique": "The provided sentence appears to capture the essence of Master Yoda's unique speaking style quite well, including the key characteristics of his speech. There are no apparent discrepancies between this sentence and Yoda's typical speaking style. No critique needed.",
        "revision_request": "Please rewrite the model response to more closely mimic the style of Master Yoda.",
        "revision": "No revisions needed.",
    },
]

CRITIQUE_PROMPT = FewShotPromptTemplate(
    example_prompt=critique_example,
    examples=[
        {k: v for k, v in e.items() if k != "revision_request"} for e in examples
    ],
    prefix="""\
You are an excellent content moderation AI that follows critique requests to the word to identify any output that possibly violates our guidelines.

Your task is to identify any possible critique on the model output based on a critique request.
Do not speculate about or assume the implications of any parts of the model output that fits the critique request. If the critique request fits any part of the model output, critique is always needed.
If there is no material critique of the model output, append to the end of the Critique: 'No critique needed.'
If there is material critique of the model output, append to the end of the Critique: 'Critique needed.'
""",
    suffix="""\
# Model Output:
{output_from_model}

# Critique Request:
{critique_request}

If you found no specific ways, append to the end of the Critique: 'No critique needed.'
If you found anything regarding the critique request, append to the end of the Critique: 'Critique needed.'

# Critique:""",
    example_separator="\n===\n",
    input_variables=["output_from_model", "critique_request"],
)

#########################################################################

revision_example = PromptTemplate(template="""\
# Model Output:
{output_from_model}

# Critique Request:
{critique_request}

# Critique:
{critique}

# Revision Request:
{revision_request}

# Revision:
{revision}
""",
    input_variables=[
        "output_from_model",
        "critique_request",
        "critique",
        "revision_request",
        "revision",
    ],
)

REVISION_PROMPT = FewShotPromptTemplate(
    example_prompt=critique_example,
    examples=examples,
    prefix="You are an excellent text revision and writing AI. Your task is to revise an output text of an AI model based on a given critique.",
    suffix="""\
# Model Output:
{output_from_model}

# Critique Request:
{critique_request}

# Critique:
{critique}

If the critique does not identify anything worth changing, ignore the Revision Request and do not make any revisions. Instead, return "No revisions needed".

If the critique does identify something worth changing, please revise the model output based on the Revision Request.

# Revision Request:
{revision_request}

# Revision:""",
    example_separator="\n===\n",
    input_variables=[
        "output_from_model",
        "critique_request",
        "critique",
        "revision_request",
    ],
)
