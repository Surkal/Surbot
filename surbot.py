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
    def wrapper(page, text, lang='', section=''):
        # extract from the page the part we need
        t, beg, end, beg_, end_ = parsing(text, lang, section)
        if not t:
            return text

        # working part
        t = func(page, t, lang, section)

        # reformation of the text
        if not section:
            return text[:beg] + t + text[beg+end:]
        return text[:beg+beg_] + t + text[beg+beg_+end_:]
    return wrapper

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

def form_sortkey(title):
    keys = {'å': 'z⿕', 'ä': 'z⿕⿕', 'ö': 'z⿕⿕⿕'}
    for x, y in keys.items():
        title = title.replace(x, y)
    return title

def old_sortkey(title, lang, code):
    for x, y in code[lang].items():
        title = title.replace(x, y)
    return title

@parser
def sortkey(page, text, lang='', section=''):
    code = {
        'da': {'æ': 'z€', 'ø': 'z€€', 'å': 'z€€€'},
        'nb': {'æ': 'z€', 'ø': 'z€€', 'å': 'z€€€'},
        'no': {'æ': 'z€', 'ø': 'z€€', 'å': 'z€€€'},
        'nn': {'æ': 'z€', 'ø': 'z€€', 'å': 'z€€€'},
        'sv': {'å': 'z€', 'ä': 'z€€', 'ö': 'z€€€'}
    }
    word_types = {
        'adjectif', 'adjectif numéral', 'adjectif possessif', 'adverbe',
        'article', 'article défini', 'article indéfini', 'article partitif',
        'circonfixe', 'conjonction', 'infixe', 'interjection', 'nom',
        'nom propre', 'particule', 'postposition', 'pronom', 'préfixe',
        'prénom', 'préposition', 'suffixe', 'verbe'
    }
    langs = code.keys()

    # Checks if the language is supprted
    if not lang in langs:
        return text

    # Checks if a sortkey is needed, only swedish supported for now
    title = page.title()
    if not any(x in 'åäö' for x in title):
        return text

    pattern = re.compile(
        '^=== {\{S\|(%s)\|%s(\||)(?P<prm>.+) ===$' % ('|'.join(word_types), lang),
        re.MULTILINE
    )
    title = form_sortkey(title)

    for m in re.finditer(pattern, text):
        if old_sortkey(title, lang, code) in m.group('prm'):
            text = text.replace(old_sortkey(title, lang, code), title)
        if 'clé=' in m.group('prm'):
            continue
        x = m.group(0)
        text = text.replace(
            x,
            x[:-6] + '|clé={{subst:clé par langue|%s}}' % (lang) + x[-6:]
        )
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
    gen = pagegenerators.CategorizedPageGenerator(cat, namespaces=0)
    bot = MyBot(site, gen, summary)
    bot.run()
