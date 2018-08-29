import re
import sys

import pywikibot
from pywikibot.bot import CurrentPageBot
from pywikibot import pagegenerators

def parser(func):
    """
    Decorator that :
    - isolates the part of the text being worked on
    - calls the function
    - then returns the complete text with the changes made

    Ideally, this decorator should be called for each function that
    modifies the wikitext.
    """
    def wrapper(page, text, lang='sv', section=''):
        # extract from the page the part we need
        t, beg, end, beg_, end_ = parsing(text, lang, section)
        if not t:
            return text

        # working part
        t = func(page, t, lang, section)

        # reformation of the page
        if not section:
            return text[:beg] + t + text[beg+end:]
        return text[:beg+beg_] + t + text[beg+beg_+end_:]
    return wrapper

def parsing(text, lang='sv', section=''):
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

def form_sortkey(title):
    keys = {'å': 'z⿕', 'ä': 'z⿕⿕', 'ö': 'z⿕⿕⿕'}
    for x, y in keys.items():
        title = title.replace(x, y)
    return title

def old_sortkey(sortkey):
    return sortkey.replace('⿕', '€')

@parser
def sortkey(page, text, lang='sv', section=''):
    supported_lang = ('sv')
    cases = {'adverbe', 'adjectif', 'nom', 'verbe'}

    # Checks if a sortkey is needed, only swedish supported for now
    title = page.title()
    if not any(x in 'åäö' for x in title):
        return text

    pattern = re.compile(
        '^=== {\{S\|(?P<type>\w+)\|(?P<lang>\w+)(\||)(?P<prm>.+) ===$',
        re.MULTILINE
    )
    title = form_sortkey(title)

    for m in re.finditer(pattern, text):
        if not m.group('lang') == lang or not m.group('lang') in supported_lang:
            continue
        if old_sortkey(title) in m.group('prm'):
            text = text.replace(old_sortkey(title), title)
        if 'clé=' in m.group('prm'):
            continue
        if not m.group('type') in cases:
            continue
        x = m.group(0)
        text = text.replace(x, x[:-6] + f'|clé={title}' + x[-6:])
    return text


class MyBot(CurrentPageBot):
    def __init__(self, site, generator, summary):
        self.site = site
        self.summary = summary
        self.generator = generator

    def run(self):
        for page in self.generator:
            self.treat(page)

    def treat(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        title = page.title()
        text = self.load(page)
        if not text:
            return

        text = sortkey(page, text)

        page.text = text
        if not page.text == page.get():
            pywikibot.showDiff(page.get(), page.text)
            page.save(summary=self.summary)

    def load(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        try:
            # Load the page
            text = page.get()
        except pywikibot.NoPage:
            pywikibot.output("Page {} does not exist; skipping."
                             .format(page.title()))
        except pywikibot.IsRedirectPage:
            pywikibot.output("Page {} is a redirect; skipping."
                             .format(page.title()))
        else:
            return text
        return None


if __name__ == '__main__':

    summary = '/* {{langue|sv}} */ clé de tri'
    site = pywikibot.Site('fr', fam='wiktionary')

    cat = pywikibot.Category(site, 'Catégorie:Verbes en suédois')
    gen = pagegenerators.CategorizedPageGenerator(cat, namespaces=0, total=100, start="assurera")
    bot = MyBot(site, gen, summary)
    bot.run()
