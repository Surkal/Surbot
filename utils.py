import re

def page_languages(text, typ):
    """
    Returns all the languages of the page, in the form of the requested type.
    It only works for the french witionary and only accept type 'list' or 'set'.
    """
    if not isinstance(typ, type):
        return None
    if not any(typ.__name__ == x for x in ('list', 'set')):
        return None
    return typ((re.findall(r"{{langue\|(?P<lang>\w+)}\}", text)))

def extract_text(filename):
    with open(filename, 'r') as f:
        return f.read()
