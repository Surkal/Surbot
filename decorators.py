import re
import json
from copy import copy
from functools import partial, update_wrapper, wraps
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

    def __call__(self, f, page, text, lang, **kwargs):
        section, new_text = '', ''
        try:
            if kwargs:
                section = kwargs['section']
        except KeyError:
            pass

        # extract from the page the part we need
        t, beg, end, beg_, end_ = self.parsing(text, lang, section)
        if not t:
            return text
        # working part
        t = self.func(page, t, lang, **kwargs)

        # reformation of the text
        if not section:
            return text[:beg] + t + text[beg+end:]
        return text[:beg+beg_] + t + text[beg+beg_+end_:]


    def __get__(self, obj, type=None):
        if obj is None:
            return self
        def bound_decorated(*args, **kwargs):
            return self.__call__(obj, *args, **kwargs)
        return bound_decorated

    def parsing(self, text, lang, section=''):
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
                with open('debug.txt', 'w') as f:
                    f.write(text)
                return text, begin, end, begin_, end_
            if not i:
                begin_, end_ = begin, end
        return text, begin_, end_, begin, end


parser = Parser


class Insert:
    filename = '/src/languages.json'

    def __init__(self, func):
        self.func = func
        self.data = self.all_languages()

    def __call__(self, page, text, lang, *args, **kwargs):
        page_langs = page_languages(text, list)

        # Whether the language is already present
        if lang in page_langs:
            return text

        text = self.category_sorting(page, text, page_langs)

        follow = ''
        for x in page_langs:
            if self.data[x]['pos'] > self.data[lang]['pos']:
                pos = self.data[x]['pos']
                follow = x
                break

        if follow:
            m = re.search(r'== {{langue\|%s' % (follow), text).start()
        else:
            m = re.search('{{clé de tri\|([^}]+)}}', text)
            if m:
                m = m.start()

        t = self.func(page, text, lang, *args, **kwargs)

        # Reformation of the text
        if not text:
            return t
        if m:
            return text[:m] + t + '\n' + text[m:]
        m = len(text)
        return text[:m] + '\n\n' + t + text[m:]

    def category_sorting(self, page, text, page_langs):
        #TODO: page_langs parameter can only be called from __call__
        names = {}
        for lang in page_langs:
            names[self.data[lang]['name']] = lang

        for line in reversed(text.split('\n')):
            # Filter
            if line.startswith('{{clé de tri|') or not line:
                continue
            if not line.startswith('[[Catégorie:'):
                break
            #
            for y in names.keys():
                if not y in line or names[y] == page_langs[-1]:
                    continue
                # In case of doubt, it's better to do nothing
                if not text.count(line) == 1:
                    continue
                text = text.replace(f'{line}\n', '')
                text = self._add_category(page, text, names[y], new_text=line)
        return text

    @parser
    def _add_category(self, *args, **kwargs):
        """Adds a category to a language section"""
        text, lang = args
        new_cat = kwargs['new_text']
        # Skip a line if not preceded by a wikilink to another category
        splitted = text.split('\n')
        if any(splitted[x].startswith('[[Catégorie:') for x in range(-1,-3,-1)):
            return text + new_cat + '\n'
        return text + '\n' + new_cat + '\n'

    def all_languages(self):
        """
        Returns all languages of the french wiktionary.
        """
        self.extract_languages()
        with open(self.filename, 'r') as f:
            return json.loads(f.read())

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
            languages[line[1].text] = {'pos': int(line[0].text),
                                       'name': line[2].text}
        languages['fr']['pos'] = -1
        with open(self.filename, 'w') as fp:
            json.dump(languages, fp, ensure_ascii=False)
        return languages


insert = Insert
