from __future__ import annotations

import unittest

from scripts.marsel_location_by_id_contract_v20_49 import clean_doc


class CleanDocTests(unittest.TestCase):
    def test_named_entity_is_preserved(self) -> None:
        self.assertEqual(clean_doc("<p>R&amp;D</p>"), "R&D")

    def test_numeric_entity_is_preserved(self) -> None:
        self.assertEqual(clean_doc("<p>&#x41;&#65;</p>"), "AA")

    def test_script_and_style_content_is_removed(self) -> None:
        self.assertEqual(
            clean_doc("<p>Visible</p><script>bad()</script><style>.x{}</style>Text"),
            "VisibleText",
        )


if __name__ == "__main__":
    unittest.main()
