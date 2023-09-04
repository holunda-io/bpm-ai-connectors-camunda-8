from typing import Tuple, Union

from langchain.chains.query_constructor.ir import Visitor, Comparator, StructuredQuery, Comparison, Operator, Operation


class AzureCognitiveSearchTranslator(Visitor):

    allowed_comparators = [
        Comparator.EQ,
        Comparator.GT,
        Comparator.GTE,
        Comparator.LT,
        Comparator.LTE,
    ]
    """Subset of allowed logical comparators."""

    allowed_operators = [Operator.AND, Operator.OR, Operator.NOT]
    """Subset of allowed logical operators."""

    def _format_func(self, func: Union[Operator, Comparator]) -> str:
        self._validate_func(func)
        map_dict = {
            Operator.OR: "or",
            Operator.NOT: "not",
            Operator.AND: "and",
            Comparator.EQ: "eq",
            Comparator.GT: "gt",
            Comparator.GTE: "ge",
            Comparator.LT: "lt",
            Comparator.LTE: "le",
        }
        return map_dict[func]

    def visit_operation(self, operation: Operation) -> str:
        args = [arg.accept(self) for arg in operation.arguments]
        operator = self._format_func(operation.operator)
        return f"({f' {operator} '.join(args)})"

    def visit_comparison(self, comparison: Comparison) -> str:
        comparator = self._format_func(comparison.comparator)
        field = comparison.attribute
        value = comparison.value
        if isinstance(value, str):
            value = f"'{value}'"
        return f"{field} {comparator} {value}"

    def visit_structured_query(self, structured_query: StructuredQuery) -> Tuple[str, dict]:
        if structured_query.filter is None:
            kwargs = {}
        else:
            kwargs = {"filters": structured_query.filter.accept(self)}
        return structured_query.query, kwargs
