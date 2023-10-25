import json
from typing import Tuple

from bs4 import BeautifulSoup, Comment, Tag, NavigableString
from playwright.async_api import Page
from playwright.sync_api import sync_playwright, expect, Locator

from bpm_ai_experimental.browser_agent.util.utils import is_interactive, truncate_str, is_visible, \
    convert_list_to_markdown, has_label

attributes_to_keep = [
    'aria-label',
    'aria-current',
    'data-name',
    'name',
    'type',
    'placeholder',
    'value',
    'role',
    'title'
]

tags_to_drop = ['script', 'style', 'link', 'meta', 'noscript']

tags_to_drop_but_keep_children = ['strong']
tags_to_drop_if_only_text_child = ['span', 'label', 'p']

interactive_tags = ['a', 'input', 'button', 'select', 'textarea']
interactive_attrs = ['onclick', 'onmousedown', 'onmouseup', 'onkeydown', 'onkeyup']

invisibility_attrs = {
    'opacity': ['', '0'],
    'display': ['none'],
    'visibility': ['hidden'],
    'aria-hidden': ['true']
}


def has_only_text_child(element):
    return all(isinstance(child, (str, NavigableString)) for child in element.children)


def has_only_text_child_and_is_to_drop(element) -> bool:
    is_tag_to_drop = element.name in tags_to_drop_if_only_text_child
    return is_tag_to_drop and not is_interactive(element) and has_only_text_child(element)


def simplify_html(html: str):
    # Parse the original HTML
    original_soup = BeautifulSoup(html, 'html.parser')
    # Create a new soup for the simplified DOM
    new_soup = BeautifulSoup('<html></html>', 'html.parser')

    # Recursive function to process elements and their children
    def process_element(element, parent):
        if isinstance(element, Comment):
            return

        # if element is just a string (NavigableString in BS4), keep it if not empty
        if isinstance(element, str):
            text = element.strip()
            if text:
                parent.append(truncate_str(text))
            return

        if not is_visible(element) or (element.name in tags_to_drop):
            return

        # Attempt to convert lists to markdown
        if element.name in ['ol', 'ul']:
            markdown = convert_list_to_markdown(element)
            if markdown:
                parent.append(markdown)
                return

        keep = (is_interactive(element) or has_label(element))

        new_element = None
        if has_only_text_child_and_is_to_drop(element) or (element.name in tags_to_drop_but_keep_children):
            new_element = parent
        elif keep or element.name == 'body':
            # Create a new element with only the allowed attributes
            new_element = Tag(name=element.name, parser=new_soup)
            for attr in attributes_to_keep:
                if attr in element.attrs:
                    new_element[attr] = element[attr]
            # If the element is interactive, convert data-testid to id
            if is_interactive(element) and 'data-testid' in element.attrs:
                new_element['id'] = element['data-testid']

        # Process children
        for child in element.children:
            process_element(child, new_element or parent)

        # If we created a new element, append it to its parent
        # but only if it has more than just an id attribute or has children
        if new_element and (len(new_element.attrs) > 1 or new_element.contents) and new_element is not parent:
            parent.append(new_element)

    # Start processing from the body of the original HTML
    process_element(original_soup.body, new_soup)

    return new_soup


##################

invisibility_attrs_json = json.dumps(invisibility_attrs)
interactive_tags = [tag.upper() for tag in interactive_tags]

js_annotate_dom = f"""
() => {{
  let currentElements = [];

  const traverseDOM = (node, pageElements) => {{
    if (node.nodeType === Node.ELEMENT_NODE) {{
      const element = node;
      const style = window.getComputedStyle(element);

      const interactive = ({interactive_tags}.includes(element.tagName) ||
        {interactive_attrs}.some(attr => element.hasAttribute(attr)) ||
        style.cursor === 'pointer');
      
      const invisibility_attrs = {invisibility_attrs_json};
      
      const visible = !Object.keys(invisibility_attrs).some(attr => 
        invisibility_attrs[attr].includes(element.getAttribute(attr)) || 
        invisibility_attrs[attr].includes(style[attr]));

      if (visible && interactive) {{
        pageElements.push(element);
        node.setAttribute('data-testid', (pageElements.length - 1).toString());
      }}
      node.setAttribute('data-interactive', interactive.toString());
      node.setAttribute('data-visible', visible.toString());
    }}

    node.childNodes.forEach(child => {{
      traverseDOM(child, pageElements);
    }});
  }};

  traverseDOM(document.documentElement, currentElements);
}}
"""


async def get_simplified_html(page: Page) -> Tuple[str, str]:
    await page.wait_for_load_state('load')
    await page.wait_for_load_state('networkidle')

    # annotate DOM with runtime information
    await page.evaluate(js_annotate_dom)

    # get HTML and simplify it
    html = await page.content()
    simplified_dom = simplify_html(html)

    # Extract the title of the page
    title = simplified_dom.title.string if simplified_dom.title else ""

    return title, simplified_dom.body.prettify()
