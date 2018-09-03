import re

from decorator import Parser


def form_sortkey(title, lang):
    code = {
        'da': {'æ': 'z⿕', 'ø': 'z⿕⿕', 'å': 'z⿕⿕⿕'},
        'nb': {'æ': 'z⿕', 'ø': 'z⿕⿕', 'å': 'z⿕⿕⿕'},
        'no': {'æ': 'z⿕', 'ø': 'z⿕⿕', 'å': 'z⿕⿕⿕'},
        'nn': {'æ': 'z⿕', 'ø': 'z⿕⿕', 'å': 'z⿕⿕⿕'},
        'sv': {'å': 'z⿕', 'ä': 'z⿕⿕', 'ö': 'z⿕⿕⿕'}
    }
    for x, y in code[lang].items():
        title = title.replace(x, y)
        title = title.replace(x.upper(), y.upper())
    return title

def old_sortkey(title, lang, code):
    for x, y in code[lang].items():
        title = title.replace(x, y)
        title = title.replace(x.upper(), y.upper())
    return title

@Parser
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
        'circonfixe', 'conjonction', 'infixe', 'interjection', 'lettre',
        'locution-phrase', 'nom', 'nom propre', 'particule', 'postposition',
        'pronom', 'préfixe', 'prénom', 'préposition', 'suffixe', 'verbe',
        'verb'
    }
    langs = code.keys()

    # Whether the language is supported
    if not lang in langs:
        return text

    # Whether a sortkey is needed
    title = page.title()
    if not any(x in 'ÅÄÖØÆåäöøæ' for x in title):
        return text

    pattern = re.compile(
        '^=== {\{S\|(%s)\|%s(\||)(?P<prm>.+) ===$' % ('|'.join(word_types), lang),
        re.MULTILINE
    )
    old = old_sortkey(title, lang, code)
    title = form_sortkey(title, lang)
    for m in re.finditer(pattern, text):
        if old in m.group('prm'):
            text = text.replace(old, '{{subst:clé par langue|%s}}' % (lang))
        if 'clé=' in m.group('prm'):
            continue
        x = m.group(0)
        text = text.replace(
            x,
            x[:-6] + '|clé={{subst:clé par langue|%s}}' % (lang) + x[-6:]
        )
    return text
