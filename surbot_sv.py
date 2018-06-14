import re
import sys

import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import CurrentPageBot

import surbot


def parser(func):
    """
    Decorator that :
    - isolates the part of the text being worked on
    - calls the function
    - then returns the complete text with the changes made

    Ideally, this decorator should be called for each function that
    modifies the wikitext.
    """
    def wrapper(page, text, section):
        p = ParserSV(page, section=section)
        try:
            t, beg, end, beg_, end_ = p.parsing()
        except TypeError:
            return text
        if not t:
            return text
        t = func(page, t, section)
        if not section:
            pass  #TODO: to complete for lang parsing
        if end == end_:
            if not beg:
                return text[:beg+beg_] + t + text[end_:]
            return text[:beg+beg_] + t + text[beg+end_:]
        return text[:beg+beg_] + t + text[beg+beg_+end_:]

    return wrapper

@parser
def uttal(page, text, section):
    title = page.title()
    # If all these code segments are in the text, nothing is touched.
    required = ('{{fr-subst-', '{{uttal|', 'ipa=', 'ljud=')
    if all(x in text for x in required):
        return text

    # Crawl and parse the fr.wikt page to extract data
    title_ = title.replace("'", "’")
    page_fr = pywikibot.Page(pywikibot.Site('fr', fam="wiktionary"), title_)
    t, _, _ = surbot.get_section(page_fr.text, lang='fr', **{'section': 'nom'})
    text_fr, _, _ = surbot.get_section(page_fr.text, lang='fr')
    if not t:
        pywikibot.output("Section not in the fr.wikt page")
        return text

    # Find the gender on the fr.wikt page
    pattern = re.compile('{{(?P<gender>(m|f|mf|mf \?|msing|fsing|mplur|\
                         fplur|p|sp))(\|équiv=(?P<equiv>.+)|)}}',
                         re.UNICODE
    )
    g = re.search(pattern, t)
    try:
        gender = g.groups('gender')[0]
    except AttributeError:
        pywikibot.output(f"Page {title} has no gender")
        return text
    if not gender in ('m', 'f', 'mf'):
        pywikibot.output("Unsupported gender")
        return text

    # For now we take easy case: regular forms with one pronounciation
    m = re.search(r'{{fr-rég\|(?P<params>.+)}}', t)
    if not m:
        return text
    params = m.groups('params')
    if not (len(params) == 1 and not '=' in params[0]):
        pywikibot.output("Inflections too complex for now")
        return text
    ipa = params[0]  #TODO: further analysis to be done

    # Check if the sound file exists on wikicommons
    sound_file = ''
    commons = pywikibot.Site('commons', fam='commons')
    commons_title = title.replace(' ', '-')
    s = pywikibot.Page(commons, 'File:Fr-' + commons_title + '.ogg')
    if s.exists():
        sound_file = 'Fr-' + commons_title + '.ogg'
    else:
        m = re.findall(r"{{écouter\|(?P<params>.+)}}", text_fr)
        if m:
            for x in range(len(m)):
                params = m[x].split('|')
                if not ('lang=fr' in params and ipa in params):
                    continue
                for p in params:
                    if p.startswith('audio='):
                        sound_file = p[6:]

    # Text editing
    if not '{{fr-subst-' in text:
        text = text.replace('{{subst|fr}}', '{{fr-subst-%s}}' % gender)
    if not '{{uttal|' in text and gender and ipa and sound_file:
        pattern = re.compile("^'''" + title + "'''( {{\w+}}|)$", re.MULTILINE)
        text = re.sub(pattern,
                      "'''%s''' {{%s}}\n*{{uttal|fr|ipa=%s|ljud=%s}}" %
                      (title, gender, ipa, sound_file),
                      text
        )
    elif not '{{uttal|' in text and gender and ipa:
        text = re.sub(re.compile("^'''" + title + "'''( {{\w+}}|)$", re.MULTILINE),
                      "'''%s''' {{%s}}\n*{{uttal|fr|ipa=%s}}" % (title, gender, ipa),
                      text
        )
    elif '{{uttal|' in text and ipa and sound_file:
        pattern = re.compile("^'''" + title + "'''( {{\w+}}|)$.*\
                             {{uttal\|fr\|ipa=" + ipa + "}}$",
                             re.MULTILINE | re.UNICODE | re.DOTALL
        )
        text = re.sub(pattern, "'''%s''' {{%s}}\n*{{uttal|fr|ipa=%s|ljud=%s}}" %
                     (title, gender, ipa, sound_file),
                     text
        )

    return text


class ParserSV:
    def __init__(self, page, lang='Franska', section=None):
        self.page = page
        self.lang = lang
        self.text = page.text
        self.section = section

    def parsing(self):
        t, beg, end = self.get_section(self.text, self.lang)
        if t and self.section:
            t, beg_, end_ = self.get_section(t, self.section)
            return t, beg, end, beg_, end_
        #TODO: to continue when self.section is None,
        #      when fixed, remove the exception in parser decorator

    def get_section(self, text, section):
        begin, end = 0, len(text)
        pattern = re.compile(f'^(?P<n>=*)( |){section}( |)=*$',
                             re.MULTILINE | re.UNICODE
        )
        s = re.search(pattern, text)
        if not s:
            return None, begin, end

        begin = s.start()
        text = text[s.start():]
        pattern = re.compile(f'^{s.groups("n")[0]}( |)(?!{section})\w+( |)=*$',
                             re.MULTILINE | re.UNICODE
        )
        s = re.search(pattern, text)
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

        pywikibot.output(f"Current page : {page.title()}")

        text = uttal(page, text, section="Substantiv")

        page.text = text

        if not page.text == page.get():
            #TODO: Sommaire bien dégueu mais pas le choix
            s = []
            if 'fr-subst' in page.text and not 'fr-subst' in page.get():
                s.append('böjn.')
            if 'ipa=' in page.text and not 'ipa=' in page.get():
                s.append('ipa')
            if 'ljud=' in page.text and not 'ljud=' in page.get():
                s.append('ljudfil')
            self.summary = '+' + ', +'.join(s)

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
    summary = 'mise en forme'
    site = pywikibot.Site('sv', fam='wiktionary')
    cat = pywikibot.Category(site, 'Kategori:Franska/Substantiv')
    gen = pagegenerators.CategorizedPageGenerator(cat)
    bot = MyBot(site, gen, summary)
    bot.run()
