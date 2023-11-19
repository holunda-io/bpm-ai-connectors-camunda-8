import re
import os
from typing import Callable, Optional, Any

# Patterns for secret replacement
SECRET_PATTERN_PARENTHESIS = re.compile(r"\{\{\s*secrets\.(?P<secret>\S+?\s*)}}")
SECRET_PATTERN_SECRETS = re.compile(r"secrets\.(?P<secret>([a-zA-Z0-9]+[\/._-])*[a-zA-Z0-9]+)")


def get_env_secret(name: str, prefix: Optional[str] = None) -> Optional[str]:
    """Get environment secret with optional prefix."""
    prefixed_name = f"{prefix}{name}" if prefix else name
    return os.environ.get(prefixed_name)


def replace_tokens(original: str, pattern: re.Pattern, converter: Callable) -> str:
    """Replace tokens in a string based on a regex pattern."""
    output = []
    last_index = 0
    for match in pattern.finditer(original):
        output.append(original[last_index:match.start()])
        output.append(converter(match))
        last_index = match.end()
    output.append(original[last_index:])
    return ''.join(output)


def resolve_secret_value(secret_replacer: Callable, match) -> Optional[str]:
    """Resolve the secret value from the replacer function."""
    secret_name = match.group("secret").strip()
    if secret_name:
        return secret_replacer(secret_name) or match.group()
    return None


def replace_secrets(
    input_str: str,
    secret_replacer: Callable = lambda name: get_env_secret(name)
) -> str:
    """Replace secrets in the input string."""
    if input_str is None:
        raise ValueError("input cannot be null")

    def replace_pattern(pattern):
        return replace_tokens(input_str, pattern, lambda m: resolve_secret_value(secret_replacer, m))

    input_str = replace_pattern(SECRET_PATTERN_PARENTHESIS)
    return replace_pattern(SECRET_PATTERN_SECRETS)


def replace_secrets_in_dict(data: dict, secret_handler: Callable = replace_secrets) -> dict:
    """Replace secrets in the values of a dictionary."""
    return {key: secret_handler(value) if isinstance(value, str) else value for key, value in data.items()}
