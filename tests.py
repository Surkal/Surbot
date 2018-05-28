import unittest
from unittest.mock import MagicMock

from surbot import MyBot, replace_templates, replace_etymology


class TestRegex(unittest.TestCase):
    def setUp(self):
        self.genders = ('n', 'c', 'f', 'm', 'mf', 'mf ?', 'msing', 'fsing', 'mplur', 'fplur', 'p', 'sp')

    def test_matching_regex(self):
        self.assertEqual(replace_templates('titta', 'blah{{sv-nom-c-or|rac-pl=titt}}blahblah'), 'blah{{sv-nom-c-or}}blahblah')
        self.assertEqual(replace_templates('titta', 'blah{{sv-nom-c-or|racine-pl=titt}}blahblah'), 'blah{{sv-nom-c-or}}blahblah')
        self.assertEqual(replace_templates('titta', 'blah{{sv-nom-c-or|nopl=oui}}blahblah'), 'blah{{sv-nom-c-ind|n=}}blahblah')

    def test_matching_regex_special_characters(self):
        self.assertEqual(replace_templates('tätla', 'blah{{sv-nom-c-or|rac-pl=tätl}}blahblah'), 'blah{{sv-nom-c-or}}blahblah')
        self.assertEqual(replace_templates('tåtla', 'blah{{sv-nom-c-or|racine-pl=tåtl}}blahblah'), 'blah{{sv-nom-c-or}}blahblah')
        self.assertEqual(replace_templates('tötla', 'blah{{sv-nom-c-or|nopl=oui}}blahblah'), 'blah{{sv-nom-c-ind|n=}}blahblah')

    def test_matching_two_same_templates(self):
        self.assertEqual(replace_templates('titla', 'blah{{sv-nom-c-or|rac-pl=titl}}bl{{sv-nom-c-or|rac-pl=titl}}ahblah'), 'blah{{sv-nom-c-or}}bl{{sv-nom-c-or}}ahblah')

    def test_matching_regex_wrong_param(self):
        self.assertEqual(replace_templates('titla', 'blah{{sv-nom-c-or|rac-pl=titla}}blahblah'), 'blah{{sv-nom-c-or|rac-pl=titla}}blahblah')
        self.assertEqual(replace_templates('titla', 'blah{{sv-nom-c-or|racine-pl=titla}}blahblah'), 'blah{{sv-nom-c-or|racine-pl=titla}}blahblah')
        self.assertEqual(replace_templates('titla', 'blah{{sv-nom-c-or|nopl=1}}blahblah'), 'blah{{sv-nom-c-or|nopl=1}}blahblah')

    def test_no_regex_match_no_change(self):
        self.assertEqual(replace_templates('titla', 'blahblahblah'), 'blahblahblah')

    def test_replace_order_gender_pron(self):
        # try all possible genders
        for gender in self.genders:
            self.assertEqual(replace_templates('titel', "'''titel''' {{%s}} {{pron||sv}}" % gender), "'''titel''' {{pron||sv}} {{%s}}" % gender)
        # unknown template, do nothing
        gender = "osef"
        self.assertEqual(replace_templates('titel', "'''titel''' {{%s}} {{pron||sv}}" % gender), "'''titel''' {{%s}} {{pron||sv}}" % gender)

    def test_replace_cf_by_compos(self):
        self.assertEqual(replace_etymology('titel', ': {{cf|av-|tjäna|lang=sv}}.\n\n'), ': {{compos|m=1|av-|tjäna|lang=sv}}.\n\n')
        # wrong language, do nothing
        self.assertEqual(replace_etymology('titel', ': {{cf|av-|tjäna|lang=nul}}.\n\n'), ': {{cf|av-|tjäna|lang=nul}}.\n\n')

    def test_add_missing_pronounciation(self):
        for gender in self.genders:
            self.assertEqual(replace_templates('titel', "'''titel''' {{%s}}" % gender), "'''titel''' {{pron||sv}} {{%s}}" % gender)
        # unknown template, do nothing
        gender = "osef"
        self.assertEqual(replace_templates('titel', "'''titel''' {{%s}}" % gender), "'''titel''' {{%s}}" % gender)


if __name__ == '__main__':
    unittest.main()
