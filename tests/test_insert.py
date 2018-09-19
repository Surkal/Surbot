from unittest import TestCase
from unittest.mock import MagicMock

import pytest

from decorators import Insert
from utils import extract_text, page_languages


@Insert
def new_entry(page, text, lang):
    return extract_text('/src/tests/page/Paris_new_text_sv.txt')

class TestLanguageInserting(TestCase):
    def setUp(self):
        self.page = MagicMock()
        self.text = extract_text('/src/tests/page/Paris.txt')

    def test_successfully_inserting_with_sortkey(self):
        self.text += "\n{{clé de tri|abcdef}}\n"
        result = extract_text('/src/tests/page/Paris_original.txt') + "\n{{clé de tri|abcdef}}\n"
        new_text = new_entry(self.page, self.text, 'sv')
        assert new_text == result

    def test_successfully_inserting_without_sortkey(self):
        new_text = new_entry(self.page, self.text, 'sv')
        assert new_text == extract_text('/src/tests/page/Paris_original.txt')


class TestCategorySorting(TestCase):
    def setUp(self):
        self.page = MagicMock()
        self.insert = Insert(MagicMock())
        self.text = extract_text('/src/tests/page/Paris.txt')
        self.langs = ['fr', 'nn', 'pt', 'ro', 'se', 'tl', 'tr', 'vi']

    def test_category_sorting_with_space(self):
        text = self.text.replace("[[Catégorie:Préfectures de France en français]]\n", '')
        text = self.insert.category_sorting(self.page, text, self.langs)
        assert "=se}}\n\n[[Catég" in text and "Nord]]\n\n== {{la" in text

    def test_category_sorting_without_space(self):
        text = self.text.replace("[[Catégorie:Capitales en same du Nord]]", "")
        text = self.insert.category_sorting(self.page, text, self.langs)
        assert "ais]]\n[[Catégorie:Préfec" in text and "nçais]]\n\n== {{la" in text

    def test_successfully_sorting(self):
        text_result = extract_text('/src/tests/page/Paris_sorted.txt')
        assert self.insert.category_sorting(self.page, self.text, self.langs) == extract_text('/src/tests/page/Paris_sorted.txt')

    def test_ending_sortkey(self):
        text = self.text + "{{clé de tri|abcdef}}\n"
        text = self.insert.category_sorting(self.page, text, self.langs)
        assert text == extract_text('/src/tests/page/Paris_sorted.txt') + "{{clé de tri|abcdef}}\n"
