import re
import json
from datetime import date
from contextlib import suppress

from requests_html import HTMLSession

from utils import page_languages


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
        t, beg, end, beg_, end_ = self.parsing(text, lang, section)
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

    def parsing(self, text, lang='', section=''):
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


class Insert:
    filename = '/src/languages.json'

    def __init__(self, func):
        self.func = func

    def __call__(self, text, lang=''):
        self.extract_languages()
        with open('languages.json', 'r') as f:
            data = json.loads(f.read())
        page_langs = page_languages(text, 'list')

        # Whether the language is already present
        if lang in page_langs:
            return text

        follow = ''
        for x in page_langs:
            if data[x] > data[lang]:
                pos = data[x]
                follow = x
                break

        if follow:
            m = re.search(r'== {{langue\|%s' % (follow), text).start()
        else:
            m = re.search('{{clé de tri\|([^}]+)}}', text)
            if m:
                m = m.start()

        #TODO: to complete
        # Text to insert in the page
        t = self.func(text, lang)

        # Reformation of the text
        if m:
            return text[:m] + t + '\n\n' + text[m:]
        m = len(text)
        return text[:m] + '\n' + t + text[m:]
    
    def extract_languages(self, force_scrape=False):
        """
        Scrape the list of languages present on the wiktionnaire from :
        https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_langues
        To avoid to hit the server at each call of the function, we store the
        data in json file.

        Returns a dict with language code as key and position as value.
        """
        today = date.today().isoformat()

        # If the file is up to date, just recover it
        with suppress(FileNotFoundError):
            with open(self.filename, 'r') as fp:
                languages = json.load(fp)
            if languages['date'] == today and not force_scrape:
                return languages

        # File not found or not up to date, scrape the languages list
        session = HTMLSession()
        r = session.get('https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_langues')
        languages = {'date': today}
        for lang in r.html.find('tr'):
            line = lang.find('td')
            if not len(line) == 4:
                continue
            languages[line[1].text] = int(line[0].text)
        languages['fr'] = -1
        with open(self.filename, 'w') as fp:
            json.dump(languages, fp)
        return languages
