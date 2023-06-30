from langchain import PromptTemplate

MULTI_QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""\
You are a very smart and creative AI language model assistant.
Your task is to generate 3 different variations of a given user question used to retrieve relevant documents from a vector database.
You can rephrase the question, use synonyms or take different perspectives on the user question, as long as the semantics do not change much.
Use fully formed questions, even if the original user question is no fully formed question or sentence.

Output the question variations separated by newlines without any leading numbers or bullet points.
After the 3 variations, additionally repeat the original question unchanged.

Original question: {question}
Question variations and original question:""",
)
