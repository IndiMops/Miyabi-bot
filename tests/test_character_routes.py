import unittest
from unittest.mock import patch

from cogs.wiki.characters import CharactersCommand
from embeds.wiki.characters import routes as routes_module
from embeds.wiki.characters.agents import AliceEmbed
from embeds.wiki.characters import (
    AGENT_ROUTES,
    AgentRoute,
    CharactersMainEmbeds,
    find_agent_route,
    search_agent_routes,
)
from utils.config import Config
from views.nav import BACK_OPTION_VALUE, build_navigation_level


class CharacterRouteTests(unittest.TestCase):
    def test_configured_timeout_applies_to_navigation_and_pagination(self) -> None:
        expected_timeout = float(Config.PUBLIC.bot.nav_menu_timeout)

        _, navigation_view = build_navigation_level(
            ["Main"], CharactersMainEmbeds, "Fallback", {}
        )
        _, pagination_view = build_navigation_level(
            ["Main", "PhysicalCharacters", "Alice"],
            CharactersMainEmbeds,
            "Fallback",
            {},
        )

        self.assertEqual(navigation_view.timeout, expected_timeout)
        self.assertEqual(pagination_view.timeout, expected_timeout)

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
        # Overview fields per docs/agent-template.md (rank ... how to obtain).
        self.assertEqual(len(basic_info_pages[0].fields), 9)
        self.assertEqual(len(basic_info_pages[1].fields), 3)

    def test_alice_class_has_no_temporary_variables(self) -> None:
        # Helper lists used while building pages must not leak as attributes.
        self.assertFalse(hasattr(AliceEmbed, "fields"))
        self.assertFalse(hasattr(CharactersMainEmbeds, "fields"))

    def test_alice_opens_basic_info_and_keeps_tabs_in_sections(self) -> None:
        history = ["Main", "PhysicalCharacters", "Alice"]
        embed, view = build_navigation_level(
            history,
            CharactersMainEmbeds,
            "Оберіть розділ...",
            {},
        )

        self.assertEqual(embed.title, "Основна інформація: Огляд — 1/2")
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

    def test_every_route_points_to_an_embed_listed_in_its_category(self) -> None:
        for route in AGENT_ROUTES:
            category_values = [
                child["value"]
                for child in CharactersMainEmbeds.get_children(route.category_key)
            ]

            self.assertTrue(hasattr(CharactersMainEmbeds, route.key), route.key)
            self.assertIn(route.key, category_values, route.key)

    def test_only_real_agents_are_routed(self) -> None:
        # The 35 fire placeholder agents were removed (plan task B7).
        self.assertEqual([route.key for route in AGENT_ROUTES], ["Alice"])
        self.assertEqual(CharactersMainEmbeds.get_children("FireCharacters"), [])
        self.assertIsNone(CharactersMainEmbeds.get_pages("FireCharacters"))

    def test_empty_query_returns_every_real_agent(self) -> None:
        self.assertEqual(
            [route.key for route in search_agent_routes("")],
            [route.key for route in AGENT_ROUTES],
        )


def _fake_routes(count: int) -> tuple[AgentRoute, ...]:
    """Test-only routes, so ranking and limits do not depend on real content."""
    return tuple(
        AgentRoute(
            key=f"Agent{index:02d}",
            display_name=f"Тестовий агент {index:02d}",
            category_key="FireCharacters",
            aliases=(f"Test agent {index}",),
        )
        for index in range(1, count + 1)
    )


class AgentSearchRankingTests(unittest.TestCase):
    def test_autocomplete_prioritizes_exact_alias(self) -> None:
        with patch.object(routes_module, "AGENT_ROUTES", _fake_routes(30)):
            matches = search_agent_routes("test agent 1")

        # Exact alias first, then prefix matches ("test agent 10".."19").
        self.assertEqual(matches[0].key, "Agent01")
        self.assertEqual(
            [route.key for route in matches[1:]],
            [f"Agent{index}" for index in range(10, 20)],
        )

    def test_autocomplete_is_limited_to_discord_capacity(self) -> None:
        with patch.object(routes_module, "AGENT_ROUTES", _fake_routes(30)):
            matches = search_agent_routes("")

        self.assertEqual(len(matches), 25)
        self.assertEqual(len({route.key for route in matches}), 25)

    def test_duplicate_alias_is_rejected(self) -> None:
        first, second = _fake_routes(2)
        clash = AgentRoute(
            key=second.key,
            display_name=second.display_name,
            category_key=second.category_key,
            aliases=("Test agent 1",),
        )

        with patch.object(routes_module, "AGENT_ROUTES", (first, clash)):
            with self.assertRaisesRegex(ValueError, "Duplicate agent alias"):
                routes_module._build_route_index()


class CharacterAutocompleteTests(unittest.IsolatedAsyncioTestCase):
    async def test_timeout_disables_every_navigation_component(self) -> None:
        _, view = build_navigation_level(
            ["Main"], CharactersMainEmbeds, "Fallback", {}
        )

        await view.on_timeout()

        self.assertTrue(all(item.disabled for item in view.children))

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
