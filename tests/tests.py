import unittest
from unittest import TestCase
from unittest.mock import MagicMock

import pytest

from decorators import Parser
from utils import extract_text
from surbot import sortkey
from sortkey import old_sortkey


class TestParsing(TestCase):
    def setUp(self):
        self.text = extract_text('tests/page/manifest.txt')
        self.p = Parser(MagicMock)

    def test_parsing_language(self):
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='sv')
        assert len(t) == 437
        assert (b, e, b_, e_) == (2316, 437, 0, 0)
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='en')
        assert len(t) == 2024
        assert (b, e, b_, e_) == (19, 2024, 0, 0)
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='ca')
        assert len(t) == 271
        assert (b, e, b_, e_) == (2044, 271, 0, 0)
        # Not existing language
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='osef')
        assert not len(t)
        assert (b, e, b_, e_) == (0, 3037, 0, 0)

    def test_parsing_section(self):
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='sv', section='adjectif')
        assert len(t) == 135
        assert (b, e, b_, e_) == (2316, 437, 68, 135)
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='sv', section='nom')
        assert len(t) == 109
        assert (b, e, b_, e_) == (2316, 437, 204, 109)
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='sv', section='dérivés')
        assert len(t) == 78
        assert (b, e, b_, e_) == (2316, 437, 314, 78)
        # Not existing section
        t, b, e, b_, e_ = self.p.parsing(self.text, lang='sv', section='apparentés')
        assert not len(t)
        assert (b, e, b_, e_) == (2316, 437, 2316, 437)


class TestSortkey(TestCase):
    def setUp(self):
        self.text = extract_text('tests/page/gå_before.txt')
        self.page = MagicMock()
        self.page.title = MagicMock(return_value='gå')
        self.langs = ('sv', 'no', 'nb', 'nn', 'da')

    def test_old_sortkey(self):
        #TODO: after class creation
        # Swedish
        titles = {'osef': 'osef', 'gå': 'gz€', 'sätta': 'sz€€tta', 'gök': 'gz€€€k', 'gångväg': 'gz€ngvz€€g'}
        for x, y in titles.items():
            assert old_sortkey(x, 'sv') == y

    def test_add_sortkey(self):
        t = sortkey(self.page, self.text, 'sv')
        with open('debug.txt', 'w') as f:
            f.write(t)
        assert t == extract_text('tests/page/gå_after_sortkey_sv.txt')
        # Sortkey already present
        p = extract_text('tests/page/gå_after_sortkey_sv.txt')
        t = sortkey(self.page, p, 'sv')
        assert t == p
        # Only one section
        p = extract_text('tests/page/gå_one_section_modified.txt')
        t = sortkey(self.page, p, 'sv', section='nom')
        assert t == p
        # Only danish sortkey
        p = extract_text('tests/page/gå_after_sortkey_da.txt')
        t = sortkey(self.page, self.text, 'da')
        assert t == p
        # 'da' and 'no' sortkeys only
        t = self.text
        p = extract_text('tests/page/gå_after_sortkey_da_no.txt')
        for x in ('da', 'no'):
            t = sortkey(self.page, t, x)
        assert t == p
        # 'da' and 'no' sortkeys only with non present languages
        t = self.text
        p = extract_text('tests/page/gå_after_sortkey_da_no.txt')
        for x in ('da', 'no', 'de', 'fr'):
            t = sortkey(self.page, t, x)
        assert t == p
        # All sortkeys
        p = extract_text('tests/page/gå_after_all_sortkeys.txt')
        for x in self.langs:
            self.text = sortkey(self.page, self.text, x)
        assert self.text == p

    def test_no_sortkey(self):
        # Wrong section
        t = sortkey(self.page, self.text, 'sv', section='dérivés')
        assert t == self.text
        # Page which doesn't need a sortkey
        p = extract_text('tests/page/manifest.txt')
        self.page.title = MagicMock(return_value='manifest')
        t = sortkey(self.page, p, 'sv')
        assert t == p


if __name__ == '__main__':
    unittest.main()
