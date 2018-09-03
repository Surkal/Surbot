import json
from datetime import date
from contextlib import suppress

from requests_html import HTMLSession


class WiktParser:
    def __init__(self, page):
        self.page = page
        self.languages = self.extract_languages()

    def extract_languages(self, filename='languages.json', force_scrape=False):
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
            with open(filename, 'r') as fp:
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
        with open('languages.json', 'w') as fp:
            json.dump(languages, fp)
        return languages



def sections(text):
    pass


if __name__ == '__main__':
    with open('Nantes.txt', 'r') as f:
        text = f.read()
    print(sections(text))
