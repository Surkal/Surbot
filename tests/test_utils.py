from unittest import TestCase

import pytest

from .utils_test import extract_text
from utils import page_languages


class TestLangList(TestCase):
    def setUp(self):
        self.text = extract_text('/src/tests/page/gå_before.txt')

    def test_no_text(self):
        assert page_languages('', 'set') == set({})
        assert page_languages('', 'list') == list()
        assert page_languages('', 'toto') == None

    def test_no_type(self):
        assert page_languages(self.text, 'toto') == None
        assert page_languages(self.text, typ='toto') == None

    def test_success(self):
        assert page_languages(self.text, 'set') == set({'da', 'no', 'sv'})
        assert page_languages(self.text, 'list') == ['da', 'no', 'sv']
