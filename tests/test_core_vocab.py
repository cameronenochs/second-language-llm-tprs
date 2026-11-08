import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import core_vocab as cv

ROW = ('<tr><td class="views-field views-field-field-display-headwords">{head}</td>'
       '<td class="views-field views-field-field-part-of-speech">{pos}</td>'
       '<td class="views-field views-field-field-frequency-rank">{rank}</td></tr>')


class CoreVocabTests(unittest.TestCase):
    def test_key_strips_macrons_and_case(self):
        self.assertEqual(cv.key(" Nāvis "), "navis")

    def test_parse_keeps_headword_and_prepositional_variants(self):
        page = (ROW.format(head="domus -ūs f.", pos="Noun: 4th Declension", rank="73")
                + ROW.format(head="ā ab abs", pos="Preposition", rank="21")
                + ROW.format(head="edō ēsse ēdī ēsum", pos="Verb: Irregular", rank="688"))
        keys = [r[0] for r in cv.parse_dcc(page)]
        self.assertEqual(keys, ["domus", "a", "ab", "abs", "edo"])

    def test_off_list_reports_first_use_in_order(self):
        items = [{"id": "x1", "lemmas": ["carrus"]}, {"id": "x2", "lemmas": ["domus", "carrus", "malum"]}]
        self.assertEqual(cv.off_list(items, {"domus"}), {"carrus": "x1", "malum": "x2"})


if __name__ == "__main__":
    unittest.main()
