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
    'aria-describedby',
    'aria-current',
    'aria-selected',
    'aria-haspopup',
    'data-name',
    'name',
    'type',
    'placeholder',
    'value',
    'role',
    'title',
    'alt',
    'href',
    'label',
    'caption',
    'summary',
    'datetime',
    'selected',
    'checked',
    'disabled',
]

tags_to_drop = ['script', 'style', 'link', 'meta', 'noscript']

tags_to_drop_but_keep_children = ['strong', 'em']
tags_to_drop_if_only_text_child = ['span', 'label', 'p']

interactive_tags = ['a', 'input', 'button', 'select', 'option', 'textarea', 'img', 'canvas', 'video', 'details', 'summary']
interactive_attrs = ['onclick', 'onmousedown', 'onmouseup', 'onkeydown', 'onkeyup', 'jsaction']
interactive_roles = ['button', 'option', 'tab', 'textarea']

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
    def process_element(element, parent, parent_in_viewport: bool):
        if isinstance(element, Comment):
            return

        # if element is just a string (NavigableString in BS4), keep it if not empty and parent is in viewport
        if isinstance(element, str):
            text = element.strip()
            if text and parent_in_viewport:
                parent.append(truncate_str(text))
            return

        if not is_visible(element) or element.name in tags_to_drop:
            return

        #if not in_viewport(element) and not has_zero_area(element):
            # some containers have zero height and/or width but their content is still visible
            # so, we only ignore subtrees of non-viewport elements if the element has an area (is an actual element)
            # the zero area container still won't be kept, but its children get a chance
            #return

        # Attempt to convert lists to markdown
        if element.name in ['ol', 'ul'] and parent_in_viewport:
            markdown = convert_list_to_markdown(element)
            if markdown:
                parent.append(markdown)
                return

        keep = (is_interactive(element) or has_label(element)) and in_viewport(element)

        new_element = None
        #if has_only_text_child_and_is_to_drop(element) or (element.name in tags_to_drop_but_keep_children):
        #    new_element = parent
        if keep or element.name == 'body':
            # Create a new element with only the allowed attributes
            new_element = Tag(name=element.name, parser=new_soup)
            for attr in attributes_to_keep:
                if attr in element.attrs and element[attr]:
                    new_element[attr] = element[attr]
            # If the element is interactive, convert data-testid to id
            if is_interactive(element) and 'data-testid' in element.attrs:
                new_element['id'] = element['data-testid']
            if 'data-value' in element.attrs:
                new_element['value'] = element['data-value']

        # Process children
        for child in element.children:
            process_element(child, new_element or parent, in_viewport(element))

        # If we created a new element, append it to its parent
        # but only if it has more than just an id attribute or has children
        #if new_element and (len(new_element.attrs) > 1 or element.contents) and new_element is not parent:
        #    parent.append(new_element)
        #else:
        #    print(f"ignoring {new_element}")
        if new_element and new_element is not parent:
            parent.append(new_element)

    # Start processing from the body of the original HTML
    process_element(original_soup.body, new_soup, True)

    return new_soup


##################

invisibility_attrs_json = json.dumps(invisibility_attrs)
interactive_tags = [tag.upper() for tag in interactive_tags]

js_annotate_dom = f"""
() => {{

    const tagElementStyles = {{
    color: "black",
    fontSize: "15px",
    padding: "3px",
    fontWeight: "bold",
    //zIndex: "999999999999",
    position: "relative",
    borderRadius: "8px",
    opacity: "0.75"
  }};
  
  function createTagElement(uniqueTag, styles) {{
      const tagElement = document.createElement("span");
    
      Object.keys(styles).forEach((styleKey) => {{
        tagElement.style[styleKey] = styles[styleKey];
      }});
    
      tagElement.textContent = uniqueTag;
      tagElement.setAttribute('data-vision-tag', 'true')
    
      return tagElement;
  }}
  
  const addTag = (element, id) => {{
      const tagElement = createTagElement(id, tagElementStyles);

      if (["input", "textarea"].includes(element.tagName.toLowerCase()) || element.getAttribute('role') === 'textbox') {{
        tagElement.style.background = "orange";
        element.parentNode.insertBefore(tagElement, element);
      }} else {{
        tagElement.style.background = "yellow";
        element.prepend(tagElement);
      }}
  }}
  
  const isElementXPercentInViewport = function(el, percentVisible) {{
    let rect = el.getBoundingClientRect(),
    windowHeight = (window.innerHeight || document.documentElement.clientHeight);
    
    return !(
      Math.floor(100 - (((rect.top >= 0 ? 0 : rect.top) / +-rect.height) * 100)) < percentVisible ||
      Math.floor(100 - ((rect.bottom - windowHeight) / rect.height) * 100) < percentVisible
    )
  }};

  let currentElements = [];

  const traverseDOM = (node, pageElements) => {{
    if (node.nodeType === Node.ELEMENT_NODE && !node.hasAttribute('data-vision-tag')) {{
      const element = node;
      const style = window.getComputedStyle(element);

      const interactive = ({interactive_tags}.includes(element.tagName) ||
        {interactive_attrs}.some(attr => element.hasAttribute(attr)) ||
        {interactive_roles}.some(role => element.getAttribute("role") == role)
        //|| style.cursor === 'pointer'
      );
      
      const invisibility_attrs = {invisibility_attrs_json};
      
      const visible = !Object.keys(invisibility_attrs).some(attr => 
        invisibility_attrs[attr].includes(element.getAttribute(attr)) || 
        invisibility_attrs[attr].includes(style[attr]));
        
      const inViewport = isElementXPercentInViewport(element, 50); 

      if (visible && interactive) {{
        pageElements.push(element);
        node.setAttribute('data-testid', (pageElements.length - 1).toString());
      }} else {{
        node.removeAttribute('data-testid');
      }}
      node.setAttribute('data-interactive', interactive.toString());
      node.setAttribute('data-visible', visible.toString());
      
      node.setAttribute('data-in-viewport', inViewport.toString());
      const rect = element.getBoundingClientRect();
      const zeroArea = (rect.width === 0 || rect.height === 0);
      node.setAttribute('data-zero-area', zeroArea.toString());
      
      // Check if the element is an input and has a value
      if ((element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') && element.value) {{
        node.setAttribute('data-value', element.value);
      }}
    }}

    node.childNodes.forEach(child => {{
      traverseDOM(child, pageElements);
    }});
  }};
  
  var elements = document.querySelectorAll('[data-vision-tag="true"]');
  elements.forEach(function(element) {{
    element.parentNode.removeChild(element);
  }});

  traverseDOM(document.documentElement, currentElements);
  
  var elements = document.querySelectorAll("[data-visible='true'][data-interactive='true'][data-testid]");
  elements.forEach(function(element) {{
    //if (!node.hasAttribute('data-vision-tagged')) {{
      addTag(element, element.getAttribute('data-testid'))
      //element.setAttribute('data-vision-tagged', 'true');
    //}}
  }});
}}
"""

x="""
function isElementPartiallyCovered(el) {
    const rect = el.getBoundingClientRect();
    let isCovered = false;

    // Function to check if the element at the point is the target element or its descendant
    function isTargetOrDescendant(el, target) {
        while (el) {
            if (el === target) {
                return true;
            }
            el = el.parentElement;
        }
        return false;
    }

    // Iterate over a set of points within the element's bounding rectangle
    for (let x = rect.left; x <= rect.right; x += 5) { // Adjust the step as needed
        for (let y = rect.top; y <= rect.bottom; y += 5) { // Adjust the step as needed
            const elementAtPoint = document.elementFromPoint(x, y);

            // If the element at the point isn't the target or its descendant, it's covered
            if (elementAtPoint && !isTargetOrDescendant(elementAtPoint, el)) {
                isCovered = true;
                break;
            }
        }
        if (isCovered) break;
    }

    return isCovered;
}
"""


js_tag_dom = f"""
() => {{
  const tagElementStyles = {{
    color: "black",
    fontSize: "15px",
    padding: "3px",
    fontWeight: "bold",
    zIndex: "999999999999",
    position: "relative",
    borderRadius: "8px",
    opacity: "0.75"
  }};
  
  function createTagElement(uniqueTag, styles) {{
      const tagElement = document.createElement("span");
    
      Object.keys(styles).forEach((styleKey) => {{
        tagElement.style[styleKey] = styles[styleKey];
      }});
    
      tagElement.textContent = uniqueTag;
    
      return tagElement;
  }}
  
  const addTag = (element, id) => {{
    const tagElement = createTagElement(id, tagElementStyles);

      if (["input", "textarea"].includes(element.tagName.toLowerCase()) || element.getAttribute('role') === 'textbox') {{
        tagElement.style.background = "orange";
        element.parentNode.insertBefore(tagElement, element);
      }} else {{
        tagElement.style.background = "yellow";
        element.prepend(tagElement);
      }}
  }}

  const elements = document.querySelectorAll(
    "a, button, input, textarea, select, option, details, summary, [role='button'], [role='textbox'], [role='tab']"
  );
  const moreElements = document.querySelectorAll(
      "a, a[href], button, input, textarea, select, option, details, summary, " +
      "[role='button'], [role='textbox'], [role='tab'], [role='link'], " +
      "[role='menuitem'], [role='slider'], [role='checkbox'], " +
      "[tabindex]:not([tabindex='-1']), " +
      "div[role='button'], span[role='button'], div[onclick], span[onclick], " +
      "area[href], [contenteditable='true'], " +
      "audio[controls], video[controls]"
  );
  var i = 1;
  elements.forEach((element) => {{
    const style = window.getComputedStyle(element);
    const invisibility_attrs = {invisibility_attrs_json};
    const visible = !Object.keys(invisibility_attrs).some(attr => 
        invisibility_attrs[attr].includes(element.getAttribute(attr)) || 
        invisibility_attrs[attr].includes(style[attr]));
        
    if (visible) {{
        element.setAttribute('data-testid', i);
        addTag(element, i);
        i++;
    }}
  }})
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


def remove_empty_tags(soup):
    for tag in soup.find_all(True):
        # Check if the tag has no children, no text, and is not img, canvas or video
        # If it has an 'id' attribute, it must also have other attributes to be kept, otherwise it is meaningless
        if not tag.contents and not tag.text.strip() and tag.name not in ["img", "canvas", "video"]:
            if 'id' in tag.attrs:
                if len(tag.attrs) == 1:
                    tag.decompose()  
            else:
                tag.decompose() 


async def get_simplified_html(browser: PlaywrightBrowser, secrets: dict) -> Tuple[str, str]:
    page = await browser.prepare_page()

    await mask_secrets(browser.page, secrets)

    # annotate DOM with runtime information
    await page.evaluate(js_annotate_dom)

    # get HTML and simplify it
    html = await page.content()
    simplified_dom = simplify_html(html)

    #remove_tags_without_attributes(simplified_dom, ["div", "span", "label", "p"])
    for tag_name in ["span", "label", "p", "strong", "em", "b"]:
        for tag in simplified_dom.find_all(tag_name, recursive=True):
            if not tag.attrs:
                tag.unwrap()

    for i in range(0, 50):
        remove_empty_tags(simplified_dom)

    # Extract the title of the page
    title = simplified_dom.title.string if simplified_dom.title else ""

    #print(simplified_dom.body.prettify() if simplified_dom.body else "EMPTY DOM")

    return title, str(simplified_dom.body) if simplified_dom.body else None#.prettify()


async def mark_interactive_dom(browser: PlaywrightBrowser):
    page = await browser.prepare_page()
    # annotate DOM with visual tags
    await page.evaluate(js_tag_dom)


js_mask_secrets = f"""
() => {{
const replaceStringInDOM = (rootElement, searchString, replacementString, caseSensitive = true) => {{
    const searchRegex = new RegExp(searchString, caseSensitive ? 'g' : 'gi');

    const replaceInElement = (element) => {{
        if (element.nodeType === Node.TEXT_NODE) {{
            element.textContent = element.textContent.replace(searchRegex, replacementString);
        }} else if (element.nodeType === Node.ELEMENT_NODE) {{
            if (element.nodeName === 'INPUT' || element.nodeName === 'TEXTAREA') {{
                element.value = element.value.replace(searchRegex, replacementString);
            }} else {{
                Array.from(element.childNodes).forEach(replaceInElement);
            }}
        }}
    }}

    replaceInElement(rootElement);
}};
"""


async def mask_secrets(page: Page, secrets: dict, reverse: bool = False):
    for k, v in secrets.items():
        if reverse:
            x = k
            k = v
            v = x
        await page.evaluate(
            js_mask_secrets + f"replaceStringInDOM(document.body, '{v}', '{k}'); }}"
        )