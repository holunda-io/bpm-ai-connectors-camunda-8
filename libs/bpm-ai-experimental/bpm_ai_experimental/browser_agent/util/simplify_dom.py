import json
from typing import Tuple

from bs4 import BeautifulSoup, Comment, Tag, NavigableString
from playwright.async_api import Page
from playwright.sync_api import sync_playwright, expect, Locator

from bpm_ai_experimental.browser_agent.util.browser import PlaywrightBrowser
from bpm_ai_experimental.browser_agent.util.injection import disable_animations, ripple_css, ripple_js
from bpm_ai_experimental.browser_agent.util.utils import is_interactive, truncate_str, is_visible, \
    convert_list_to_markdown, has_label, in_viewport, has_zero_area

attributes_to_keep = [
    'aria-label',
    'aria-current',
    'data-name',
    'name',
    'type',
    'placeholder',
    'value',
    'role',
    'title',
    'alt'
]

tags_to_drop = ['script', 'style', 'link', 'meta', 'noscript']

tags_to_drop_but_keep_children = ['strong', 'em']
tags_to_drop_if_only_text_child = ['span', 'label', 'p']

interactive_tags = ['a', 'input', 'button', 'select', 'textarea', 'img']
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
    new_soup.title = original_soup.title

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

        if not is_visible(element) or element.name in tags_to_drop:
            return

        if not in_viewport(element) and not has_zero_area(element):
            # some containers have zero height and/or width but their content is still visible
            # so, we only ignore subtrees of non-viewport elements if the element has an area (is an actual element)
            # the zero area container still won't be kept, but its children get a chance
            return

        # Attempt to convert lists to markdown
        if element.name in ['ol', 'ul']:
            markdown = convert_list_to_markdown(element)
            if markdown:
                parent.append(markdown)
                return

        keep = (is_interactive(element) or has_label(element)) and in_viewport(element)

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
            if 'data-value' in element.attrs:
                new_element['value'] = element['data-value']

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
  
  const isElementXPercentInViewport = function(el, percentVisible) {{
    let rect = el.getBoundingClientRect(),
    windowHeight = (window.innerHeight || document.documentElement.clientHeight);
    
    return !(
      Math.floor(100 - (((rect.top >= 0 ? 0 : rect.top) / +-rect.height) * 100)) < percentVisible ||
      Math.floor(100 - ((rect.bottom - windowHeight) / rect.height) * 100) < percentVisible
    )
  }};
  
  const elementIsVisibleInViewport = (el, partiallyVisible = false) => {{
    const rect = el.getBoundingClientRect();
    const innerHeight = (window.innerHeight || document.documentElement.clientHeight);
    const innerWidth = (window.innerWidth || document.documentElement.clientWidth);
    return partiallyVisible
        ? ((rect.top > 0 && rect.top < innerHeight) ||
            (rect.bottom > 0 && rect.bottom < innerHeight)) &&
            ((rect.left > 0 && rect.left < innerWidth) || (rect.right > 0 && rect.right < innerWidth))
        : rect.top >= 0 && rect.left >= 0 && rect.bottom <= innerHeight && rect.right <= innerWidth;
  }};
  
  const isElementInViewport = (el, percentVisible) => {{
    if (!el) {{
      return false;
    }}

    const rect = el.getBoundingClientRect();
    const windowHeight = (window.innerHeight || document.documentElement.clientHeight);
    const windowWidth = (window.innerWidth || document.documentElement.clientWidth);

    // Check if the element has zero width and height
    if (rect.width === 0 && rect.height === 0) {{
        return true; // The element is not visible if it has no size, but whatever...
    }}

    // Calculate visible dimensions, considering if width or height is zero
    var visibleWidth = rect.width === 0 ? 0 : Math.max(0, Math.min(rect.right, windowWidth)) - Math.max(0, rect.left);
    var visibleHeight = rect.height === 0 ? 0 : Math.max(0, Math.min(rect.bottom, windowHeight)) - Math.max(0, rect.top);
    
    // For elements with zero width or height, we treat the visible dimension as 1 pixel if it's within the viewport
    visibleWidth = visibleWidth <= 0 ? (rect.height > 0 ? 1 : 0) : visibleWidth;
    visibleHeight = visibleHeight <= 0 ? (rect.width > 0 ? 1 : 0) : visibleHeight;
    
    // Calculate the area of the element and the visible area
    const elementArea = rect.width * rect.height || 1; // Prevent division by zero by defaulting to 1 if both dimensions are zero
    const visibleArea = visibleWidth * visibleHeight;
    
    // Calculate the percentage of the element that is visible
    const visiblePercentage = (visibleArea / elementArea) * 100;
    
    return (visiblePercentage > percentVisible);
  }}

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
      
      const inViewport = isElementXPercentInViewport(element, 1); //isElementInViewport(element, 1);
      node.setAttribute('data-in-viewport', inViewport.toString());
      const rect = element.getBoundingClientRect();
      const zeroArea = (rect.width === 0 || rect.height === 0);
      node.setAttribute('data-zero-area', zeroArea.toString());
      
      // Check if the element is an input and has a value
      if (element.tagName.toLowerCase() === 'input' && element.value) {{
        node.setAttribute('data-value', element.value);
      }}
    }}

    node.childNodes.forEach(child => {{
      traverseDOM(child, pageElements);
    }});
  }};

  traverseDOM(document.documentElement, currentElements);
}}
"""


def remove_tags_without_attributes(soup, tags_to_remove):
    # Collect all tags that match the criteria in a list
    def collect_tags(tag, tags_to_remove):
        tags_to_unwrap = []
        for child in tag.find_all(recursive=False):
            if child.name in tags_to_remove and not child.attrs:
                tags_to_unwrap.append(child)
            else:
                # Recursively check the children of this tag
                tags_to_unwrap.extend(collect_tags(child, tags_to_remove))
        return tags_to_unwrap

    # Get the list of tags to unwrap
    tags_to_unwrap = collect_tags(soup, tags_to_remove)

    # Unwrap the tags
    for tag in tags_to_unwrap:
        tag.unwrap()


async def get_simplified_html(browser: PlaywrightBrowser) -> Tuple[str, str]:
    page = await browser.prepare_page()

    # annotate DOM with runtime information
    await page.evaluate(js_annotate_dom)

    # get HTML and simplify it
    html = await page.content()
    simplified_dom = simplify_html(html)

    remove_tags_without_attributes(simplified_dom, ["div", "span"])

    # Extract the title of the page
    title = simplified_dom.title.string if simplified_dom.title else ""

    #print(simplified_dom.body.prettify())

    return title, simplified_dom.body#.prettify()
