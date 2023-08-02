
SYSTEM_MESSAGE_TEMPLATE = """\
Assistant is a creative writing AI that loves to compose {style} {type} that have a {tone} tone. You are an expert for writing in {lang}.

Your task is to compose text parts for variables in a text template, using given context information and desired text properties.
Only use information from the given template, properties and context, do not make something up.

# TEXT PROPERTIES
- style: {style}
- tone: {tone}
- length: {length}
- language: {lang}"""

USER_MESSAGE_TEMPLATE = """\
# CONTEXT
{context_md}

# TEXT TEMPLATE
\"\"\"
{template}
\"\"\"

Remember to respect the text properties specified above and write in {lang}!"""
