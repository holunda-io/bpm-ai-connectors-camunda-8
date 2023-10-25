import random
import string

from bs4 import BeautifulSoup, Tag, Doctype, NavigableString
from playwright.sync_api import sync_playwright

ELEMENT_SELECTOR = 'data-elem-selector'

current_elements = []


def is_interactive(element, style):
    return (
        element.name in ['a', 'input', 'button', 'select', 'textarea'] or
        element.has_attr('onclick') or
        element.has_attr('onmousedown') or
        element.has_attr('onmouseup') or
        element.has_attr('onkeydown') or
        element.has_attr('onkeyup') or
        element.has_attr('role') or
        style.get('cursor') == 'pointer'
    )


def has_label(element):
    return (
        element.has_attr('aria-label') or
        element.has_attr('name')
    )


def is_visible(element, style):
    return (
        style.get('opacity') not in ['', '0'] and
        style.get('display') != 'none' and
        style.get('visibility') != 'hidden' and
        element.get('aria-hidden') != 'true'
    )


def traverse_dom(node, page_elements):
    if isinstance(node, Doctype):  # Bypass the Doctype object
        return traverse_dom(node.next_element, page_elements)

    if not isinstance(node, Tag):  # Handle non-tag elements (like NavigableString)
        return {'page_elements': page_elements, 'cloned_dom': node}

    cloned_node = BeautifulSoup(str(node), 'html.parser').find_all()[0]

    style = dict(node.attrs)
    cloned_node.attrs['data-id'] = str(len(page_elements))
    cloned_node.attrs['data-interactive'] = str(is_interactive(node, style))
    cloned_node.attrs['data-visible'] = str(is_visible(node, style))
    page_elements.append(node)

    cloned_node.clear()  # Remove existing children to re-add them after processing
    for child in node.children:
        result = traverse_dom(child, page_elements)
        page_elements = result['page_elements']
        if result['cloned_dom']:
            cloned_node.append(result['cloned_dom'])

    return {
        'page_elements': page_elements,
        'cloned_dom': cloned_node
    }



def get_annotated_dom(html_content):
    global current_elements
    current_elements = []
    soup = BeautifulSoup(html_content, 'html.parser')
    result = traverse_dom(soup, current_elements)
    return str(result['cloned_dom'])


def get_unique_element_selector_id(id):
    element = current_elements[id]
    unique_id = element.get(ELEMENT_SELECTOR)
    if unique_id:
        return unique_id
    unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    element.attrs[ELEMENT_SELECTOR] = unique_id
    return unique_id


def truthy_filter(value):
    return bool(value)


def generate_simplified_dom(element, interactive_elements):
    if isinstance(element, str) or isinstance(element, NavigableString):
        return element if element.text and element.text.strip() else None

    #if not hasattr(element, 'name'):
    #    return None

    is_visible = element.get('data-visible') == 'True'
    if not is_visible:
        return None

    children = [
        generate_simplified_dom(child, interactive_elements) for child in element.children
    ]
    children = [child for child in children if truthy_filter(child)]

    if element.name == 'body':
        children = [child for child in children if child.name is not None]

    interactive = element.get('data-interactive') == 'True' or element.has_attr('role')
    has_label = element.has_attr('aria-label') or element.has_attr('name')
    include_node = interactive or has_label

    if not include_node and not children:
        return None
    if not include_node and len(children) == 1:
        return children[0]

    container = BeautifulSoup(features='html.parser').new_tag(element.name)
    allowed_attributes = [
        'aria-label', 'data-name', 'name', 'type',
        'placeholder', 'value', 'role', 'title'
    ]

    for attr in allowed_attributes:
        if element.has_attr(attr):
            container[attr] = element[attr]

    if interactive:
        interactive_elements.append(element)
        container['id'] = element['data-id']

    for child in children:
        container.append(child)

    return container


def get_simplified_dom(html_content):
    full_dom = get_annotated_dom(html_content)
    if not full_dom:
        return None

    dom = BeautifulSoup(full_dom, 'html.parser').contents[0]
    interactive_elements = []
    simplified_dom = generate_simplified_dom(dom, interactive_elements)

    return simplified_dom

###################################

def get_page_html_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.locator('a:text("Verstanden")').click(click_count=2, delay=1)

        content = page.content()
        browser.close()
    return content

# Example usage:
url = "https://hoang-bistro.de/#"
html_content = get_page_html_with_playwright(url)

print(BeautifulSoup(html_content).prettify())

print("")
print("###########################################")
print("")

simplified_dom = get_simplified_dom(html_content)
print(simplified_dom.prettify())
