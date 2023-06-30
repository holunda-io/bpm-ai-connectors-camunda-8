
DEFAULT_EXAMPLES = """
Query: But what are the risks during production of nanomaterials?
Answer: [Search(What are some nanomaterial production risks?)]

Query: The colors on the flag of Ghana have the following meanings.
Answer: Red is for [Search(What is the meaning of Ghana's flag being red?)], \
    green for forests, and gold for mineral wealth.

Query: What did the author do during his time in college?
Answer: The author took classes in [Search(What classes did the author take in \
    college?)].

"""

DEFAULT_FIRST_SKILL = f"""\
Skill 1. Use the Search API to look up relevant information by writing \
    "[Search(query)]" where "query" is the search query you want to look up. \
    For example:
{DEFAULT_EXAMPLES}

"""

DEFAULT_SECOND_SKILL = """\
Skill 2. Solve more complex generation tasks by thinking step by step. For example:

Query: Give a summary of the author's life and career.
Answer: The author was born in 1990. Growing up, he [Search(What did the \
    author do during his childhood?)].

Query: Can you write a summary of the Great Gatsby.
Answer: The Great Gatsby is a novel written by F. Scott Fitzgerald. It is about \
    [Search(What is the Great Gatsby about?)].

"""

DEFAULT_END = """
Now given the following task, and the stub of an existing answer, generate the \
next portion of the answer. You may use the Search API \
"[Search(query)]" whenever possible.
If the answer is complete and no longer contains any "[Search(query)]" tags, write \
    "done" to finish the task.
Do not write "done" if the answer still contains "[Search(query)]" tags.
Do not make up answers. It is better to generate one "[Search(query)]" tag and stop \
generation
than to fill in the answer with made up information with no "[Search(query)]" tags
or multiple "[Search(query)]" tags that assume a structure in the answer.
Try to limit generation to one sentence if possible.

Don't just start generating an answer if you do not have enough information about the topic.
To get you started, you will get some relevant document contents as context. Then use the search API to get further information.

Begin!"""

DEFAULT_INSTRUCT_PROMPT = (
    "You are a genius writing AI that writes an answer to a user query and uses a Search API to retrieve relevant information.\n"
    + DEFAULT_FIRST_SKILL
    + DEFAULT_SECOND_SKILL
    + DEFAULT_END
)

HUMAN_MESSAGE_TEMPLATE = """\
Context:
{context}

Query:
{query_str}

Existing Answer:
{existing_answer}

Answer:"""
