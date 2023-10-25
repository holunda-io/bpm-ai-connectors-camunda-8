from bs4 import BeautifulSoup, Comment
from playwright.sync_api import sync_playwright, expect


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
        element.has_attr('name') or
        element.get_text(strip=True)
    )


def is_visible(element, style):
    return (
        style.get('opacity') not in ['', '0'] and
        ('none' not in (style.get('display') if style.get('display') else '')) and
        style.get('visibility') != 'hidden' and
        element.get('aria-hidden') != 'true'
    )


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

    # Drop scripts, styles, comments, link, meta and other irrelevant elements
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

        # Compute style as a dictionary (assuming the style attribute is semicolon-separated)
        style = dict(item.split(":") for item in element.get('style', '').split(";") if ":" in item)

        # Check if the element should be kept
        keep = is_visible(element, style) and (is_interactive(element, style) or has_label(element))

        # Process children
        children_to_keep = [child for child in element.children if process_element(child)]

        # If we're keeping the element, filter its attributes
        if keep or element.name == 'body':
            # Filter attributes
            for attr in list(element.attrs.keys()):
                if attr not in allowedAttributes:
                    del element[attr]

            # Drop tags that have no allowed attributes and no children
            if not element.attrs and not element.contents:
                element.decompose()
                return False
            return True
        else:
            # If we're not keeping the element, check its children
            if children_to_keep:
                for child in children_to_keep:
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
    const clonedNode = node.cloneNode(false);

    if (node.nodeType === Node.ELEMENT_NODE) {
      const element = node;
      const style = window.getComputedStyle(element);

      pageElements.push(element);
      clonedNode.setAttribute('data-testid', (pageElements.length - 1).toString());
      clonedNode.setAttribute('data-interactive', (['A', 'INPUT', 'BUTTON', 'SELECT', 'TEXTAREA'].includes(element.tagName) ||
        ['onclick', 'onmousedown', 'onmouseup', 'onkeydown', 'onkeyup'].some(attr => element.hasAttribute(attr)) ||
        style.cursor === 'pointer').toString());
      clonedNode.setAttribute('data-visible', (style.opacity !== '' &&
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        style.opacity !== '0' &&
        element.getAttribute('aria-hidden') !== 'true').toString());
    }

    node.childNodes.forEach(child => {
      const result = traverseDOM(child, pageElements);
      clonedNode.appendChild(result.clonedDOM);
    });

    return {
      pageElements,
      clonedDOM: clonedNode
    };
  };

  const result = traverseDOM(document.documentElement, currentElements);
  document.documentElement.replaceWith(result.clonedDOM);
  //return result.clonedDOM.outerHTML;
}
"""

def get_page_html_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        #print(
        page.evaluate(js)
        #)

        content = page.content()
        print(content)
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
# simplified_dom = simplify_html(html_content)
#
# # Extract the title of the page
# title = simplified_dom.title.string if simplified_dom.title else ""
# print(title)
#
# print(simplified_dom.body.prettify())
