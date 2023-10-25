from bs4 import BeautifulSoup, Comment
from playwright.sync_api import sync_playwright, expect


def is_interactive(element):
    return element.get('data-interactive') == 'true'


def has_label(element):
    return (
        element.has_attr('aria-label') or
        element.has_attr('name') or
        element.get_text(strip=True)
    )


def is_visible(element):
    return element.get('data-visible') == 'true'


allowedAttributes = [
    #'aria-label',
    'aria-current',
    'data-name',
    'name',
    'type',
    'placeholder',
    'value',
    'role',
    'title',
]


def simplify_html(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')

    # Drop scripts, styles, link, meta and other irrelevant elements
    for tag in soup(['script', 'style', 'link', 'meta']):
        tag.decompose()

    # Drop comments
    for comment in soup.findAll(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Recursive function to process elements and their children
    def process_element(element):
        # Base case: if element is just a string (NavigableString in BS4), keep it
        if isinstance(element, str):
            return bool(element.strip())  # Only retain non-whitespace text

        if not is_visible(element):
            element.decompose()
            return False

        # Check if the element should be kept
        keep = (is_interactive(element) or has_label(element))

        # Process children
        children_to_keep = [child for child in element.children if process_element(child)]

        # If we're keeping the element, filter its attributes
        if keep or element.name == 'body':
            # Filter attributes
            for attr in list(element.attrs.keys()):
                if attr not in allowedAttributes:
                    del element[attr]

            # Convert data-testid to id for interactive elements
            if is_interactive(element) and 'data-testid' in element.attrs:
                element['id'] = element['data-testid']

            # Remove data attributes
            for data_attr in ['data-interactive', 'data-testid', 'data-visible']:
                if data_attr in element.attrs:
                    del element[data_attr]

            # Drop tags that have no allowed attributes and no children
            if (not element.attrs or (len(element.attrs)) == 1 and element.has_attr('id')) and not element.contents:
                element.decompose()
                return False
            return True
        else:
            # If we're not keeping the element, check its children
            if children_to_keep:
                for child in children_to_keep:
                    if not isinstance(child, str) or is_visible(element):  # don't keep text if direct parent is not visible
                        element.insert_before(child)
            # Remove the original element
            element.decompose()
            return False

    # Start processing from the body of the HTML
    body = soup.body
    if body:
        process_element(body)
    return soup


##################


js = """
() => {
  let currentElements = [];

  const traverseDOM = (node, pageElements) => {
    if (node.nodeType === Node.ELEMENT_NODE) {
      const element = node;
      const style = window.getComputedStyle(element);

      pageElements.push(element);
      node.setAttribute('data-testid', (pageElements.length - 1).toString());
      node.setAttribute('data-interactive', (['A', 'INPUT', 'BUTTON', 'SELECT', 'TEXTAREA'].includes(element.tagName) ||
        ['onclick', 'onmousedown', 'onmouseup', 'onkeydown', 'onkeyup'].some(attr => element.hasAttribute(attr)) ||
        style.cursor === 'pointer').toString());
      node.setAttribute('data-visible', (style.opacity !== '' &&
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        style.opacity !== '0' &&
        element.getAttribute('aria-hidden') !== 'true').toString());
    }

    node.childNodes.forEach(child => {
      traverseDOM(child, pageElements);
    });
  };

  traverseDOM(document.documentElement, currentElements);
}
"""

def get_page_html_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # annotate DOM
        page.evaluate(js)

        content = page.content()
        browser.close()
    return content


# Example usage:
url = "https://hoang-bistro.de/produkt-kategorie/alokoholfreie-getraenke/"
html_content = get_page_html_with_playwright(url)
#
# #print(BeautifulSoup(html_content).prettify())
#
# print("")
# print("###########################################")
# print("")
#
simplified_dom = simplify_html(html_content)

# Extract the title of the page
title = simplified_dom.title.string if simplified_dom.title else ""
print(title)

print(simplified_dom.body.prettify())
