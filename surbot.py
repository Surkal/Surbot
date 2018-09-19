import re
import sys
from types import MethodType
from datetime import datetime, timedelta

import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import CurrentPageBot

from sortkey import sortkey
from utils import page_languages


class MyBot(CurrentPageBot):
    def __init__(self, site, generator, summary, langs=('sv')):
        self.site = site
        self.summary = summary
        self.generator = generator
        self.supported = set(langs)

    def langs(self, text):
        text_langs = page_languages(text, set)
        return self.supported.intersection(text_langs)

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

        pywikibot.output(title)

        # Fix a sortkey
        for lang in self.langs(text):
            text = sortkey(page, text, lang=lang)

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

    summary = 'ajout clé de tri'
    site = pywikibot.Site('fr', fam='wiktionary')

    cat = pywikibot.Category(site, 'Catégorie:suédois')
    gen = pagegenerators.CategorizedPageGenerator(cat, namespaces=0)

    # recent changes, last 48 hours
    end = datetime.now() - timedelta(hours=24)
    gen = pagegenerators.RecentChangesPageGenerator(site=site, namespaces=0,
                                                    showBot=False, end=end)
    bot = MyBot(site, gen, summary, langs=('sv', 'no', 'da', 'nn', 'nb', 'fi'))
    bot.run()
