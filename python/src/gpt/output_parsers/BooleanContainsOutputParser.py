from langchain.schema import BaseOutputParser


class BooleanContainsOutputParser(BaseOutputParser[bool]):
    true_tag: str = "YES"
    false_tag: str = "NO"

    def parse(self, text: str) -> bool:
        """Parse the output of an LLM call to a boolean based on given true/false equivalent tags.
        One of the tags must be present somewhere in the model output. If none or both are present, an exception is raised.

        Args:
            text: output of language model

        Returns:
            boolean

        """
        text = text.upper()
        true_tag = self.true_tag.upper()
        false_tag = self.false_tag.upper()

        if ((true_tag not in text) and (false_tag not in text)) or (true_tag in text and false_tag in text):
            raise ValueError(
                f"BooleanOutputParser expected output value to either be "
                f"{self.true_tag} or {self.false_tag}. Received {text}."
            )
        return true_tag in text

    @property
    def _type(self) -> str:
        """Snake-case string identifier for output parser type."""
        return "boolean_contains_output_parser"
