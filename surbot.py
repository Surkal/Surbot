import re
import sys
import argparse
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
            text = sortkey(None, page, text, lang=lang)

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


def main(*args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-simulate",
        help="option for test purposes",
        default=False,
        action="store_true"
    )
    parser.add_argument(
        "-site",
        help="Site on which the bot is working",
        default='fr',
        type=str
    )
    parser.add_argument(
        "-summary",
        help="Summary",
        default="Mise en forme",
        type=str
    )
    parser.add_argument(
        "-r",
        help="goes through the pages modified by humans in the last 24 hours",
        default=24,
        action="store_true"
    )
    parser.add_argument(
        "--recent",
        help="goes through the pages modified by humans in the last X hours",
        default=0,
        type=float
    )
    parser.add_argument(
        "-cat",
        help="Category to crawl",
        type=str
    )
    args = parser.parse_args()

    pywikibot.config.simulate = args.simulate

    summary = args.summary
    site = pywikibot.Site(args.site, fam='wiktionary')

    if args.r or args.recent:
        t = args.recent or args.r
        end = datetime.now() - timedelta(hours=t)
        gen = pagegenerators.RecentChangesPageGenerator(site=site, namespaces=0,
                                                        showBot=False, end=end,
                                                        topOnly=True)

    if args.cat:
        cat = pywikibot.Category(site, f'Catégorie:{args.cat}')
        gen = pagegenerators.CategorizedPageGenerator(cat, namespaces=0)

    bot = MyBot(site, gen, summary, langs=('sv', 'no', 'da', 'nn', 'nb', 'fi'))
    bot.run()

if __name__ == '__main__':

    main(sys.argv)
