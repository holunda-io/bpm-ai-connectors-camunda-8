from bs4 import NavigableString

def is_interactive(element):
    return element.get('data-interactive') == 'true'


def has_label(element):
    return (
        element.has_attr('aria-label') or
        element.has_attr('name') or
        (len(element.get_text(strip=True)) > 0)
    )


def is_visible(element):
    return element.get('data-visible') == 'true'


def truncate_str(s, n=100):
    """Limit the string to at most n characters and add '[…]' at the end if it's truncated."""
    if len(s) <= n:
        return s
    return s[:n-3] + '[…]'


def convert_list_to_markdown(element, truncate_to=100):
    if element.name not in ['ol', 'ul'] or is_interactive(element):
        return None

    markdown_list = []
    prefix = '*' if element.name == 'ul' else None

    for idx, li in enumerate(element.find_all('li', recursive=False), start=1):
        # Check if the li contains only text and no other elements
        if all(isinstance(child, str) for child in li.children) and not is_interactive(li):
            text = li.get_text(strip=True)
            text = truncate_str(text, truncate_to) if truncate_to else text
            if prefix:
                markdown_list.append(f"{prefix} {text}")
            else:
                markdown_list.append(f"{idx}. {text}")
        else:
            # Not a simple list, return None
            return None

    return "\n".join(markdown_list)