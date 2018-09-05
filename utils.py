import re

def page_languages(text, typ):
    """
    Returns all the languages of the page, in the form of the requested type.
    It only works for the french witionary and only accept type 'list' or 'set'.
    """
    if not typ in ('list', 'set'):
        return None
    if typ == 'set':
        return set(re.findall(r"{{langue\|(?P<lang>\w+)}\}", text))
    return list(re.findall(r"{{langue\|(?P<lang>\w+)}\}", text))
