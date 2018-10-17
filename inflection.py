import re

from requests_html import HTMLSession
import pywikibot

from sortkey import sortkey
from decorators import Insert


class Inflection:
    """
    Create an inflection entry on the french wiktionary.
    Only works for swedish nouns and non existing entry.
    """
    @Insert
    def add_inflection(page, text, lang, *args, **kwargs):
        text = """== {{langue|%s}} ==\n=== {{S|nom|%s|flexion}} ===""" % (lang, lang)
        if kwargs['table']:
            text += f"\n{kwargs['table']}"
        text += """\n'''{{subst:PAGENAME}}''' {{pron||sv}}\n# ''%s de'' {{lien|%s|%s}}.\n""" % args
        return text

    @classmethod
    def inflection(self, page, title, lang):
        site_fr = pywikibot.Site('fr', fam='wiktionary')
        site_sv = pywikibot.Site('sv', fam='wiktionary')
        inflections = {}
        cases = {
            'sv': ('sing-def', 'plur-indef', 'plur-def')
        }
        case_name = {
            'sing-def' : "Singulier défini",
            'plur-indef' : "Pluriel indéfini",
            'plur-def': "Pluriel défini"
        }
        session = HTMLSession()
        r = session.get(f'https://fr.wiktionary.org/wiki/{title}')
        for c in cases[lang]:
            inflections[c] = list(x.text for x in r.html.find(f'.{c} .lang-{lang} a'))

        # table
        table = None
        if page.text.count('{{sv-nom-') == 1:
            table = re.search(r'{{sv-nom-([^}]+)}}', page.text).group()
            table = table[:-2] + f'|mot={title}' + '}}'

        for c, names in inflections.items():
            c = case_name[c]
            for name in names:
                # Already in the fr wiktionary?
                page_fr = pywikibot.Page(site_fr, name)
                if f'langue|{lang}' in page_fr.text:
                    continue
                # If not in the sv wiktionary, give up
                if not f'böjning|sv|subst|{title}' in pywikibot.Page(site_sv, name).text:
                    continue

                t = self.add_inflection(page_fr, page_fr.text, lang, c, title, lang, table=table)
                if page_fr.text == t:
                    continue
                t = sortkey(page_fr, t, lang)
                page_fr.text = t
                try:
                    pywikibot.showDiff(page_fr.get(), page_fr.text)
                except pywikibot.exceptions.NoPage:
                    pywikibot.showDiff('', page_fr.text)
                page_fr.save(
                    summary="/* {{langue|%s}} */ Ajout flexion" % lang,
                    watch=True,
                    minor=False,
                )
