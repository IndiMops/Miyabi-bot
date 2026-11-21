"""Walk the whole /characters navigation tree and check it against Discord limits.

Every node reachable from "Main" is visited, so a new agent or section is
covered automatically: the level must build, its select must fit Discord's
limits, its embeds must fit the embed limits, page numbers must match the
real page counts, and images must use stable https links.
"""

import math
import re
import unittest

import discord

from embeds.general import MAX_PAGE_LINKS
from embeds.wiki.characters import AGENT_ROUTES, CharactersMainEmbeds
from views.nav import MAX_SELECT_OPTIONS, build_navigation_level

TREE = CharactersMainEmbeds
ROOT = "Main"

# Discord limits (https://discord.com/developers/docs/resources/message#embed-object-embed-limits).
EMBED_TITLE_LIMIT = 256
EMBED_DESCRIPTION_LIMIT = 4096
EMBED_FIELD_COUNT_LIMIT = 25
EMBED_FIELD_NAME_LIMIT = 256
EMBED_FIELD_VALUE_LIMIT = 1024
EMBED_FOOTER_LIMIT = 2048
EMBED_AUTHOR_LIMIT = 256
EMBED_TOTAL_LIMIT = 6000
SELECT_OPTION_TEXT_LIMIT = 100  # label, value and description
SELECT_PLACEHOLDER_LIMIT = 150
LINK_LABEL_LIMIT = 80

PAGE_NUMBER = re.compile(r" — (\d+)/(\d+)$")
ANNOUNCED_PAGES = re.compile(r"— (\d+) стор")
DISCORD_ATTACHMENT = re.compile(r"(?:media|cdn)\.discordapp\.(?:net|com)/attachments/")
CUSTOM_EMOJI = re.compile(r"^<a?:\w{2,32}:\d{17,20}>$")


def _child_value(child) -> str:
    if isinstance(child, dict):
        return child["value"]
    if isinstance(child, tuple):
        return child[1]
    return child


def walk_tree() -> dict[str, list[str]]:
    """Return every reachable key with the first history that leads to it."""
    histories = {ROOT: [ROOT]}
    queue = [ROOT]
    while queue:
        key = queue.pop(0)
        for child in TREE.get_children(key):
            value = _child_value(child)
            if value not in histories:
                histories[value] = [*histories[key], value]
                queue.append(value)
    return histories


def node_embeds(key: str) -> list[discord.Embed]:
    return [TREE.get_embed(key), *(TREE.get_pages(key) or [])]


def all_embeds() -> list[discord.Embed]:
    unique: dict[int, discord.Embed] = {}
    for key in walk_tree():
        for embed in node_embeds(key):
            unique.setdefault(id(embed), embed)
    return list(unique.values())


class NavigationTreeStructureTests(unittest.TestCase):
    def test_every_child_points_to_an_embed(self) -> None:
        for key in walk_tree():
            with self.subTest(key=key):
                self.assertTrue(hasattr(TREE, key), f"{key} has no embed attribute")
                self.assertIsInstance(TREE.get_embed(key), discord.Embed)
                for page in TREE.get_pages(key) or []:
                    self.assertIsInstance(page, discord.Embed)

    def test_tree_contains_the_known_branches(self) -> None:
        keys = set(walk_tree())

        self.assertTrue(
            {
                "PhysicalCharacters",
                "FireCharacters",
                "IceCharacters",
                "ElectricCharacters",
                "EtherCharacters",
                "Alice",
            }
            <= keys
        )

    def test_agent_routes_follow_real_tree_paths(self) -> None:
        for route in AGENT_ROUTES:
            with self.subTest(route=route.key):
                history = route.history
                self.assertEqual(history[0], ROOT)
                for parent, child in zip(history, history[1:]):
                    self.assertIn(
                        child,
                        [_child_value(item) for item in TREE.get_children(parent)],
                        f"{child} is not a child of {parent}",
                    )

    def test_child_options_fit_select_limits(self) -> None:
        for key in walk_tree():
            for child in TREE.get_children(key):
                if not isinstance(child, dict):
                    continue
                with self.subTest(key=key, child=child.get("value")):
                    for name in ("label", "value", "description"):
                        text = child.get(name) or ""
                        self.assertLessEqual(len(text), SELECT_OPTION_TEXT_LIMIT, name)
                    self.assertTrue(child["label"].strip())
                    emoji = child.get("emoji")
                    if emoji:
                        self.assertTrue(
                            CUSTOM_EMOJI.match(emoji)
                            or (not emoji.startswith("<") and len(emoji) <= 8),
                            f"invalid emoji {emoji!r}",
                        )

            placeholder = TREE.get_placeholder(key, "")
            self.assertLessEqual(len(placeholder), SELECT_PLACEHOLDER_LIMIT, key)


class NavigationTreeEmbedTests(unittest.TestCase):
    def test_embeds_fit_discord_limits(self) -> None:
        for embed in all_embeds():
            with self.subTest(title=embed.title):
                self.assertLessEqual(len(embed.title or ""), EMBED_TITLE_LIMIT)
                self.assertLessEqual(len(embed.description or ""), EMBED_DESCRIPTION_LIMIT)
                self.assertLessEqual(len(embed.fields), EMBED_FIELD_COUNT_LIMIT)
                for field in embed.fields:
                    self.assertTrue(field.name, "empty field name")
                    self.assertTrue(field.value, "empty field value")
                    self.assertLessEqual(len(field.name), EMBED_FIELD_NAME_LIMIT)
                    self.assertLessEqual(len(field.value), EMBED_FIELD_VALUE_LIMIT)
                self.assertLessEqual(len(embed.footer.text or ""), EMBED_FOOTER_LIMIT)
                self.assertLessEqual(len(embed.author.name or ""), EMBED_AUTHOR_LIMIT)
                self.assertLessEqual(len(embed), EMBED_TOTAL_LIMIT)

    def test_images_use_stable_https_links(self) -> None:
        for embed in all_embeds():
            urls = {
                "image": embed.image.url,
                "thumbnail": embed.thumbnail.url,
                "author icon": embed.author.icon_url,
                "footer icon": embed.footer.icon_url,
            }
            for kind, url in urls.items():
                if not url:
                    continue
                with self.subTest(title=embed.title, kind=kind):
                    self.assertTrue(url.startswith("https://"), url)
                    self.assertIsNone(DISCORD_ATTACHMENT.search(url), url)

    def test_page_links_are_valid_link_buttons(self) -> None:
        for embed in all_embeds():
            links = getattr(embed, "links", ())
            with self.subTest(title=embed.title):
                self.assertLessEqual(len(links), MAX_PAGE_LINKS)
                for label, url in links:
                    self.assertTrue(0 < len(label) <= LINK_LABEL_LIMIT, label)
                    self.assertTrue(url.startswith("https://"), url)

    def test_page_numbers_match_real_page_counts(self) -> None:
        numbered_ids: set[int] = set()
        for key in walk_tree():
            pages = TREE.get_pages(key) or []
            if len(pages) < 2:
                continue
            for index, page in enumerate(pages, start=1):
                numbered_ids.add(id(page))
                with self.subTest(key=key, title=page.title):
                    match = PAGE_NUMBER.search(page.title or "")
                    self.assertIsNotNone(match, "a multi-page section needs ' — N/M'")
                    self.assertEqual(
                        (int(match.group(1)), int(match.group(2))),
                        (index, len(pages)),
                    )

        # A single page (or a page outside a paginated list) must not claim "N/M".
        for embed in all_embeds():
            if id(embed) in numbered_ids:
                continue
            with self.subTest(title=embed.title):
                self.assertIsNone(PAGE_NUMBER.search(embed.title or ""))

    def test_announced_page_counts_match_targets(self) -> None:
        for key in walk_tree():
            for child in TREE.get_children(key):
                if not isinstance(child, dict):
                    continue
                announced = ANNOUNCED_PAGES.search(child.get("description") or "")
                if announced is None:
                    continue
                target = child["value"]
                with self.subTest(tab=target):
                    pages = TREE.get_pages(target) or [TREE.get_embed(target)]
                    self.assertEqual(int(announced.group(1)), len(pages))


class NavigationTreeViewTests(unittest.IsolatedAsyncioTestCase):
    async def test_every_level_builds_a_valid_select(self) -> None:
        for key, history in walk_tree().items():
            children_count = len(TREE.get_children(key))
            page_size = MAX_SELECT_OPTIONS - int(len(history) > 1)
            option_pages = max(1, math.ceil(children_count / page_size))

            for option_page in range(option_pages):
                with self.subTest(history=history, option_page=option_page):
                    embed, view = build_navigation_level(
                        history, TREE, "Fallback", {key: option_page}
                    )
                    self.assertIsInstance(embed, discord.Embed)

                    selects = [
                        item for item in view.children
                        if isinstance(item, discord.ui.Select)
                    ]
                    self.assertEqual(len(selects), 1)
                    options = selects[0].options
                    self.assertGreater(len(options), 0)
                    self.assertLessEqual(len(options), MAX_SELECT_OPTIONS)
                    values = [option.value for option in options]
                    self.assertEqual(len(values), len(set(values)), "duplicate values")
                    view.stop()


if __name__ == "__main__":
    unittest.main()
