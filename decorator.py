import re


def parsing(text, lang='', section=''):
    #TODO: does not support subsections present several times
    regex = {
        0 : r'=* *{{langue\|' + lang + '}}',
        1 : r'\n== *{{langue\|(?!' + lang + r'}).*} *=',
        2 : r'=* *{{S\|' + section + r'(\||})',
        3 : r'\n=* *{{S\|(?!' + section + r').*}} *='
    }
    begin, end = 0, len(text)
    begin_, end_ = 0, 0
    # Isolate language
    for i in range(2):
        s = re.search(regex[2*i], text)
        if not s:
            return '', begin, end, begin_, end_
        begin = s.start()
        text = text[begin:]
        m = re.search(regex[(2*i)+1], text)
        if m:
            end = m.start()
            text = text[:end]
        if not section:
            return text, begin, end, begin_, end_
        if not i:
            begin_, end_ = begin, end
    return text, begin_, end_, begin, end


class Parser:
    """
    Decorator that :
    - isolates the part of the text being worked on
    - calls the function
    - then returns the complete text with the changes made

    Ideally, this decorator should be called for each function that
    modifies the wikitext.
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, page, text, lang='', section=''):
        # extract from the page the part we need
        t, beg, end, beg_, end_ = parsing(text, lang, section)
        if not t:
            return text

        # working part
        t = self.func(page, t, lang, section)

        # reformation of the text
        if not section:
            return text[:beg] + t + text[beg+end:]
        return text[:beg+beg_] + t + text[beg+beg_+end_:]

    def __get__(self, instance, cls):
        # Return a Method if it is called on an instance
        return self if instance is None else MethodType(self, instance)
