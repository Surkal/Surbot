import re
import sys

import pywikibot
from pywikibot.bot import CurrentPageBot
from pywikibot import pagegenerators


def parser(func):
    def wrapper(fn, title, text, **kwargs):
        t, beg, end = get_section(text, **kwargs)
        # If section not found, give up
        if not t:
            pywikibot.output(f"Section {kwargs['section']} not found")
            return text
        t = fn(title, t)
        return text[:beg] + t + text[(beg+end):]
    return wrapper

@parser
def modify_wikitext(fn, title, text, **kwargs):
    return text

def replace_templates(title, text):
    """Brings templates up to standard."""
    # New lua module no longer requires "rac-pl" and "racine-pl" parameters
    m = re.search(r"{{sv-nom-c-or\|(rac-pl|racine-pl)=(?P<root>[a-z-äöå]+)}}",
                  text)
    if m and m.group('root') == title[:-1] and title.endswith('a'):
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

    return text

def create_inflection(inflection, case, title):
    #TODO: add template 'voir' if necessary
    inflection.text = """== {{langue|sv}} ==
=== {{S|nom|sv|flexion}} ===
{{sv-nom-c-or|mot=%s}}
'''{{subst:PAGENAME}}''' {{pron||sv}}
# ''%s de'' {{lien|%s|sv}}.""" % (title, case, title)
    #inflection.save(summary="forme conjuguée")

def get_inflections(site, page):
    title = page.title()
    root = title[:-1]
    infl = {
        'Singulier défini': 'an',
        'Pluriel indéfini': 'or',
        'Pluriel défini': 'orna'
    }
    for key, value in infl.items():
        inflection = pywikibot.Page(site, root + value)
        if not inflection.exists():
            if not page in list(inflection.getReferences()):
                pywikibot.output(f"Problème de déclinaisons sur la page {title}")
                continue
            create_inflection(inflection, key, title)
            continue
        pywikibot.output(f"Page {root+value} already exists.")
        with open('page_to_create.txt', 'a') as f:
            f.write(f"{title}, {root+value}\n")

def replace_etymology(title, text):
    # replace {{cf}} by {{compos}}
    word1, word2 = '', ''
    text = re.sub(r"{{cf\|(?P<word1>[a-z-äöå]+)\|(?P<word2>[a-z-äöå]+)\|lang=sv}}",
                  "{{compos|m=1|\g<word1>|\g<word2>|lang=sv}}",
                  text,
    )
    return text

def get_section(text, lang='sv', **kwargs):
    begin, end = 0, len(text)
    if not kwargs:
        s = re.search(r'=* *{{langue\|' + lang + '}}', text)
    else:
        s = re.search(r'=* *{{S\|' + kwargs['section'] + r'(\||})', text)
    if not s:
        return None, begin, end

    begin = s.start()
    text = text[s.start():]
    if not kwargs:
        s = re.search(r'\n== *{{langue\|(?!' + lang + r'}).*} *=', text)
    else:
        s = re.search(r'\n=* *{{S\|(?!' + kwargs['section'] + r').*}} *=', text)
    if s:
        end = s.start()
        text = text[:s.start()]
    return text, begin, end


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

        # Filters special pages and words not ending by letter "a"
        if not title.endswith('a') or ':' in title:
            return

        # Analyze and modify (or not) the wikitext
        pywikibot.output(f"Current page : {title}")
        text = modify_wikitext(replace_templates, title, text)
        text = modify_wikitext(replace_etymology, title, text, **{'section': 'étymologie'})

        if '{{sv-nom-c-or}}' in text:
            get_inflections(self.site, page)

        page.text = text

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
    #TODO: Detecter les verbes à particule
    summary = 'mise en forme'
    site = pywikibot.Site('fr', fam='wiktionary')
    #page = pywikibot.Page(site, 'Modèle:sv-nom-c-or')
    #gen = page.getReferences()
    cat = pywikibot.Category(site, 'Catégorie:suédois')
    gen = pagegenerators.CategorizedPageGenerator(cat)
    bot = MyBot(site, gen, summary)
    bot.run()
