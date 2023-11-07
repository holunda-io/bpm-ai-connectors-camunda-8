from inspect import signature
from typing import Any, Optional, Dict, Callable, Type, Union

from pydantic import BaseModel, validate_call, create_model


def _create_subset_model(
    name: str, model: BaseModel, field_names: list
) -> Type[BaseModel]:
    """Create a pydantic model with only a subset of model's fields."""
    fields = {}
    for field_name in field_names:
        field = model.model_fields[field_name]
        fields[field_name] = (field.annotation.__origin__, field)
    return create_model(name, **fields)


def _get_filtered_args(
    inferred_model: Type[BaseModel],
    func: Callable,
) -> dict:
    """Get the arguments from a function's signature."""
    schema = inferred_model.model_json_schema()["properties"]
    valid_keys = signature(func).parameters
    return {k: schema[k] for k in valid_keys}


class _SchemaConfig:
    """Configuration for the pydantic model."""
    arbitrary_types_allowed: bool = True


def create_schema_from_function(
    model_name: str,
    func: Callable,
) -> Type[BaseModel]:
    """Create a pydantic schema from a function's signature.
    Args:
        model_name: Name to assign to the generated pydandic schema
        func: Function to generate the schema from
    Returns:
        A pydantic model with the same arguments as the function
    """
    validated = validate_call(func, config=_SchemaConfig)  # type: ignore
    inferred_model = validated.__pydantic_core_schema__
    print(inferred_model)
    # Pydantic adds placeholder virtual fields we need to strip
    valid_properties = _get_filtered_args(inferred_model, func)
    return _create_subset_model(
        f"{model_name}Schema", inferred_model, list(valid_properties)
    )


class Function(BaseModel):

    name: str
    """
    The unique name of the tool that clearly communicates its purpose.
    """

    description: str
    """
    A description of what the function does, used by the model to choose when and how to use the tool.
    """

    args_schema: Optional[Dict[str, Any]] = None
    """Function's input argument schema."""

    callable: Callable

    @classmethod
    def from_callable(
        cls,
        name: str,
        description: str,
        args_schema: Union[Dict[str, Any], Type[BaseModel]],
        callable: Callable
    ):
        return cls(
           name=name,
            description=description,
            args_schema=args_schema if isinstance(args_schema, dict) else args_schema.model_json_schema()["properties"],
            callable=callable
        )


