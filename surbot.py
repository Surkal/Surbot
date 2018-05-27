import re

import pywikibot
from pywikibot.bot import CurrentPageBot


def replace_templates(title, text):
    """Brings templates up to standard."""
    # New lua module no longer requires "rac-pl" and "racine-pl" parameters
    m = re.search(r"{{sv-nom-c-or\|(rac-pl|racine-pl)=(?P<root>[a-z-äöå]+)}}", text)
    if m and m.group('root') == title[:-1]:
        text = text.replace(m.group(), "{{sv-nom-c-or}}")

    # Uncountable nouns must use the appropriate template : {{sv-nom-c-ind}}
    text = re.sub(r"{{sv-nom-c-or\|nopl=oui}}", "{{sv-nom-c-ind|n=}}", text)

    # {{genre}} {{pron}} -> {{pron}} {{genre}}
    word, gender = '', ''
    genders = '(?P<gender>(n|c|f|m|mf|mf \?|msing|fsing|mplur|fplur|p|sp))'
    text = re.sub(r"'''(?P<word>[a-z-äöå]+)''' {{" + genders + "}} {{pron\|\|sv}}",
                  "'''\g<word>''' {{pron||sv}} {{\g<gender>}}",
                  text,
    )

    # Add missing pronounciation template on the page
    text = re.sub(r"'''(?P<word>[a-z-äöå]+)''' {{" + genders + "}}",
                  "'''\g<word>''' {{pron||sv}} {{\g<gender>}}",
                  text,
    )

    # replace {{cf}} by {{compos}}
    word1, word2 = '', ''
    text = re.sub(r"{{cf\|(?P<word1>[a-z-äöå]+)\|(?P<word2>[a-z-äöå]+)\|lang=sv}}",
                  "{{compos|m=1|\g<word1>|\g<word2>|lang=sv}}",
                  text,
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
        text = self.load(page)
        if not text:
            return

        # Filters special pages and words not ending by letter "a"
        if not page.title().endswith('a') or ':' in page.title():
            return
        # Analyze and modify (or not) the wikitext
        page.text = replace_templates(page.title(), text)

        if not page.text == page.get():
            page.save(summary=self.summary)
            pywikibot.showDiff(page.get(), page.text)

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
    summary = 'supprime paramètre devenu inutile'
    site = pywikibot.Site('fr', fam='wiktionary')
    model = pywikibot.Page(site, 'Modèle:sv-nom-c-or')
    gen = model.getReferences(total=40)
    bot = MyBot(site, gen, summary)
    bot.run()
