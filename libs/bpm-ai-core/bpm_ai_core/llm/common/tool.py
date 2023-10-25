from typing import Any, Optional, Dict


class Tool:

    name: str
    """
    The unique name of the tool that clearly communicates its purpose.
    """

    description: str
    """
    A description of what the function does, used by the model to choose when and how to use the tool.
    """

    args_schema: Optional[Dict[str, Any]] = None
    """Tool's input argument schema."""


