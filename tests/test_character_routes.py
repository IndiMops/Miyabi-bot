import unittest

from cogs.wiki.characters import CharactersCommand
from embeds.wiki.characters import (
    AGENT_ROUTES,
    CharactersMainEmbeds,
    find_agent_route,
    search_agent_routes,
)
from views.nav import BACK_OPTION_VALUE, build_navigation_level


class CharacterRouteTests(unittest.TestCase):
    def test_alice_has_expected_paginated_sections(self) -> None:
        expected_page_counts = {
            "AliceBasicInfo": 2,
            "AliceCombatMechanics": 3,
            "AliceSkills": 6,
            "AliceMindscapeCinema": 3,
            "AliceProgression": 4,
            "AliceProfile": 4,
        }

        self.assertEqual(
            [option["value"] for option in CharactersMainEmbeds.Alice_children],
            list(expected_page_counts),
        )
        for section, page_count in expected_page_counts.items():
            self.assertEqual(
                len(CharactersMainEmbeds.get_pages(section)),
                page_count,
            )

        basic_info_pages = CharactersMainEmbeds.get_pages("AliceBasicInfo")
        self.assertEqual(len(basic_info_pages[0].fields), 7)
        self.assertEqual(len(basic_info_pages[1].fields), 1)

    def test_alice_opens_basic_info_and_keeps_tabs_in_sections(self) -> None:
        history = ["Main", "PhysicalCharacters", "Alice"]
        embed, view = build_navigation_level(
            history,
            CharactersMainEmbeds,
            "Оберіть розділ...",
            {},
        )

        self.assertEqual(embed.title, "Основна інформація — 1/2")
        alice_select = next(
            item for item in view.children if hasattr(item, "options")
        )
        self.assertEqual(
            alice_select.placeholder,
            "Оберіть розділ про Алісу...",
        )
        self.assertEqual(
            [option.value for option in alice_select.options],
            [
                "AliceBasicInfo",
                "AliceCombatMechanics",
                "AliceSkills",
                "AliceMindscapeCinema",
                "AliceProgression",
                "AliceProfile",
                BACK_OPTION_VALUE,
            ],
        )

        _, section_view = build_navigation_level(
            [*history, "AliceCombatMechanics"],
            CharactersMainEmbeds,
            "Оберіть розділ...",
            {},
        )
        section_select = next(
            item for item in section_view.children if hasattr(item, "options")
        )
        self.assertEqual(
            section_select.placeholder,
            "Оберіть розділ про Алісу...",
        )
        self.assertEqual(
            [option.value for option in section_select.options],
            [option.value for option in alice_select.options],
        )

    def test_each_navigation_level_can_define_its_placeholder(self) -> None:
        _, main_view = build_navigation_level(
            ["Main"], CharactersMainEmbeds, "Fallback", {}
        )
        _, physical_view = build_navigation_level(
            ["Main", "PhysicalCharacters"],
            CharactersMainEmbeds,
            "Fallback",
            {},
        )

        main_select = next(
            item for item in main_view.children if hasattr(item, "options")
        )
        physical_select = next(
            item for item in physical_view.children if hasattr(item, "options")
        )
        self.assertEqual(main_select.placeholder, "Оберіть атрибут агента...")
        self.assertEqual(
            physical_select.placeholder,
            "Оберіть фізичного агента...",
        )

    def test_finds_agent_by_key_and_aliases(self) -> None:
        self.assertEqual(find_agent_route("Alice").key, "Alice")
        self.assertEqual(find_agent_route("  АЛІСА  ").key, "Alice")
        self.assertEqual(
            find_agent_route("alice thymefield").key,
            "Alice",
        )

    def test_unknown_agent_returns_none(self) -> None:
        self.assertIsNone(find_agent_route("Unknown Agent"))

    def test_route_contains_full_back_navigation_history(self) -> None:
        route = find_agent_route("Аліса")

        self.assertEqual(
            route.history,
            ["Main", "PhysicalCharacters", "Alice"],
        )

    def test_fire_routes_point_to_existing_embeds(self) -> None:
        fire_routes = [
            route
            for route in AGENT_ROUTES
            if route.category_key == "FireCharacters"
        ]

        self.assertEqual(len(fire_routes), 35)
        self.assertTrue(
            all(hasattr(CharactersMainEmbeds, route.key) for route in fire_routes)
        )

    def test_autocomplete_prioritizes_exact_alias(self) -> None:
        matches = search_agent_routes("fire agent 30")

        self.assertTrue(matches)
        self.assertEqual(matches[0].key, "FireAgent30")

    def test_autocomplete_is_limited_to_discord_capacity(self) -> None:
        matches = search_agent_routes("")

        self.assertEqual(len(matches), 25)
        self.assertEqual(len({route.key for route in matches}), 25)


class CharacterAutocompleteTests(unittest.IsolatedAsyncioTestCase):
    async def test_command_exposes_agent_autocomplete(self) -> None:
        command = CharactersCommand.characters
        choices = await CharactersCommand(None).agent_autocomplete(
            None,
            "алі",
        )

        self.assertEqual(
            [parameter.name for parameter in command.parameters],
            ["agent"],
        )
        self.assertIsNotNone(command.parameters[0].autocomplete)
        self.assertEqual(choices[0].name, "Аліса Таймфілд")
        self.assertEqual(choices[0].value, "Alice")


if __name__ == "__main__":
    unittest.main()
