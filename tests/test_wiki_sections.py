"""Tests for the shared agent section helpers (embeds/wiki/characters/sections.py)."""

import unittest

import discord

from embeds.wiki.characters.sections import Section, pages_label, section


class PagesLabelTests(unittest.TestCase):
    def test_ukrainian_plural_forms(self) -> None:
        expected = {
            1: "1 сторінка",
            2: "2 сторінки",
            4: "4 сторінки",
            5: "5 сторінок",
            11: "11 сторінок",
            12: "12 сторінок",
            14: "14 сторінок",
            21: "21 сторінка",
            22: "22 сторінки",
            25: "25 сторінок",
        }
        for count, label in expected.items():
            with self.subTest(count=count):
                self.assertEqual(pages_label(count), label)


class SectionTests(unittest.TestCase):
    def test_multi_page_section_numbers_its_pages(self) -> None:
        pages = [discord.Embed(title="Огляд"), discord.Embed(title="Характеристики")]

        result = section("Info", "Основна інформація", "Огляд персонажа", pages)

        self.assertEqual(
            [page.title for page in result.pages],
            [
                "Основна інформація: Огляд — 1/2",
                "Основна інформація: Характеристики — 2/2",
            ],
        )
        self.assertEqual(
            result.tab,
            {
                "label": "Основна інформація",
                "value": "Info",
                "description": "Огляд персонажа — 2 сторінки",
            },
        )

    def test_single_page_section_has_no_number(self) -> None:
        result = section("Combat", "Бойові механіки", "Особливості бою", [discord.Embed(title="Стиль гри")])

        self.assertEqual(result.pages[0].title, "Бойові механіки: Стиль гри")
        self.assertEqual(result.tab["description"], "Особливості бою — 1 сторінка")

    def test_section_needs_pages(self) -> None:
        with self.assertRaises(ValueError):
            Section(key="Empty", label="Порожньо", summary="—", pages=())


if __name__ == "__main__":
    unittest.main()
