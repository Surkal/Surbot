import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from .utils import extract_text
from surbot import parsing, sortkey, form_sortkey, parser


class TestParsing(TestCase):
    def setUp(self):
        self.text = extract_text('tests/page/manifest.txt')

    def test_parsing_language(self):
        t, b, e, b_, e_ = parsing(self.text, lang='sv')
        self.assertEqual(len(t), 437)
        self.assertEqual((b, e, b_, e_), (2316, 437, 0, 0))
        t, b, e, b_, e_ = parsing(self.text, lang='en')
        self.assertEqual(len(t), 2024)
        self.assertEqual((b, e, b_, e_), (19, 2024, 0, 0))
        t, b, e, b_, e_ = parsing(self.text, lang='ca')
        self.assertEqual(len(t), 271)
        self.assertEqual((b, e, b_, e_), (2044, 271, 0, 0))
        # Not existing language
        t, b, e, b_, e_ = parsing(self.text, lang='osef')
        self.assertEqual(len(t), 0)
        self.assertEqual((b, e, b_, e_), (0, 3037, 0, 0))

    def test_parsing_section(self):
        t, b, e, b_, e_ = parsing(self.text, lang='sv', section='adjectif')
        self.assertEqual(len(t), 135)
        self.assertEqual((b, e, b_, e_), (2316, 437, 68, 135))
        t, b, e, b_, e_ = parsing(self.text, lang='sv', section='nom')
        self.assertEqual(len(t), 109)
        self.assertEqual((b, e, b_, e_), (2316, 437, 204, 109))
        t, b, e, b_, e_ = parsing(self.text, lang='sv', section='dérivés')
        self.assertEqual(len(t), 78)
        self.assertEqual((b, e, b_, e_), (2316, 437, 314, 78))
        # Not existing section
        t, b, e, b_, e_ = parsing(self.text, lang='sv', section='apparentés')
        self.assertEqual(len(t), 0)
        self.assertEqual((b, e, b_, e_), (2316, 437, 2316, 437))


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
        #for x, y in titles.items():
            #self.assertEqual(form_sortkey(x), y)

    def test_add_sortkey(self):
        t = sortkey(self.page, self.text, lang='sv')
        self.assertEqual(t, extract_text('tests/page/gå_after_sortkey_sv.txt'))
        # Sortkey already present
        p = extract_text('tests/page/gå_after_sortkey_sv.txt')
        t = sortkey(self.page, p, lang='sv')
        self.assertEqual(t, p)
        # Only one section
        p = extract_text('tests/page/gå_one_section_modified.txt')
        t = sortkey(self.page, p, lang='sv', section='nom')
        self.assertEqual(t, p)
        # Only danish sortkey
        p = extract_text('tests/page/gå_after_sortkey_da.txt')
        t = sortkey(self.page, self.text, lang='da')
        self.assertEqual(t, p)
        # 'da' and 'no' sortkeys only
        t = self.text
        p = extract_text('tests/page/gå_after_sortkey_da_no.txt')
        for x in ('da', 'no'):
            t = sortkey(self.page, t, lang=x)
        self.assertEqual(t, p)
        # 'da' and 'no' sortkeys only with non present languages
        t = self.text
        p = extract_text('tests/page/gå_after_sortkey_da_no.txt')
        for x in ('da', 'no', 'de', 'fr'):
            t = sortkey(self.page, t, lang=x)
        self.assertEqual(t, p)
        # All sortkeys
        p = extract_text('tests/page/gå_after_all_sortkeys.txt')
        for x in self.langs:
            self.text = sortkey(self.page, self.text, lang=x)
        self.assertEqual(self.text, p)

    def test_no_sortkey(self):
        # Wrong section
        t = sortkey(self.page, self.text, lang='sv', section='dérivés')
        self.assertEqual(t, self.text)
        # Page which doesn't need a sortkey
        p = extract_text('tests/page/manifest.txt')
        self.page.title = MagicMock(return_value='manifest')
        t = sortkey(self.page, p, lang='sv')
        self.assertEqual(t, p)


class TestParser(TestCase):
    def test_global(self):
        func = MagicMock()


if __name__ == '__main__':
    unittest.main()
