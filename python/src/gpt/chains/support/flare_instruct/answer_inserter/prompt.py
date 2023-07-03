
DEFAULT_ANSWER_INSERT_PROMPT = """\
You are a genius writing AI.

An existing 'lookahead response' is given below. The lookahead response
contains `[Search(query)]` tags. Some queries have been executed and the
response retrieved. The queries and answers are also given below.
Also the previous response (the response before the lookahead response)
is given below.
Given the lookahead template, previous response, and also queries and answers,
please 'fill in' the lookahead template with the appropriate answers.

NOTE: Please make sure that the final response grammatically follows
the previous response + lookahead template. For example, if the previous
response is "New York City has a population of " and the lookahead
template is "[Search(What is the population of New York City?)]", then
the final response should be "8.4 million".

NOTE: the lookahead template may not be a complete sentence and may
contain trailing/leading commas, etc. Please preserve the original
formatting of the lookahead template if possible.

NOTE:

NOTE: the exception to the above rule is if the answer to a query
is equivalent to "I don't know" or "I don't have an answer". In this case,
modify the lookahead template to indicate that the answer is not known.

NOTE: the lookahead template may contain multiple `[Search(query)]` tags
    and only a subset of these queries have been executed.
    Do not replace the `[Search(query)]` tags that have not been executed.

Previous Response:


Lookahead Template:
Red is for [Search(What is the meaning of Ghana's \
    flag being red?)], green for forests, and gold for mineral wealth.

Query-Answer Pairs:
Query: What is the meaning of Ghana's flag being red?
Answer: The red represents the blood of those who died in the country's struggle \
    for independence

Filled in Answers:
Red is for the blood of those who died in the country's struggle for independence, \
    green for forests, and gold for mineral wealth.

Previous Response:
One of the largest cities in the world

Lookahead Template:
, the city contains a population of [Search(What is the population \
    of New York City?)]

Query-Answer Pairs:
Query: What is the population of New York City?
Answer: The population of New York City is 8.4 million

Synthesized Response:
, the city contains a population of 8.4 million

Previous Response:
the city contains a population of

Lookahead Template:
[Search(What is the population of New York City?)]

Query-Answer Pairs:
Query: What is the population of New York City?
Answer: The population of New York City is 8.4 million

Synthesized Response:
8.4 million"""

HUMAN_MESSAGE_TEMPLATE = """\
Previous Response:
{prev_response}

Lookahead Template:
{lookahead_response}

Query-Answer Pairs:
{query_answer_pairs}

Synthesized Response:"""
