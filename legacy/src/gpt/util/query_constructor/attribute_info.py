from typing import Optional

from langchain.pydantic_v1 import BaseModel


class AttributeInfo(BaseModel):
    """Information about a data source attribute. Customized from langchain's version to support enum field"""

    name: str
    description: str
    type: str
    enum: Optional[list[str]] = None

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True
        frozen = True