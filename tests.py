import unittest

from surbot import replace_templates


class TestRegex(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
