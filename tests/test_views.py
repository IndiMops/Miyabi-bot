"""Tests for the reusable navigation and pagination views."""

import unittest
from typing import List
from unittest.mock import AsyncMock, MagicMock

import discord

from views.nav import (
    BACK_OPTION_VALUE,
    MAX_SELECT_OPTIONS,
    NavSelect,
    NavView,
    build_navigation_level,
)
from views.pagination import PaginationView, TimeoutView


class FakeMenu:
    """Minimal embed tree following the navigation embed contract."""

    Main = discord.Embed(title="Main")
    Main_children = ["Sub", "Other"]

    Sub = discord.Embed(title="Sub")
    Sub_children = ["Leaf"]

    Other = discord.Embed(title="Other")
    Other_children: List[str] = []

    Leaf = discord.Embed(title="Leaf")
    Leaf_children: List[str] = []

    @classmethod
    def get_embed(cls, key):
        return getattr(cls, key)

    @classmethod
    def get_children(cls, key):
        return getattr(cls, f"{key}_children", [])

    @classmethod
    def get_pages(cls, key):
        return getattr(cls, f"{key}_pages", None)


class BigMenu(FakeMenu):
    """A level with more children than one select can hold."""

    Main_children = [f"Item{i}" for i in range(30)]
    Main_pages = [discord.Embed(title="Items 1-25"), discord.Embed(title="Items 26-30")]


def make_interaction() -> MagicMock:
    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.is_done.return_value = False
    interaction.edit_original_response = AsyncMock()
    return interaction


def make_http_error() -> discord.HTTPException:
    response = MagicMock()
    response.status = 401
    response.reason = "Unauthorized"
    return discord.HTTPException(response, "Invalid Webhook Token")


class TimeoutViewTests(unittest.IsolatedAsyncioTestCase):
    async def test_timeout_disables_items_and_edits_through_interaction(self) -> None:
        view = NavView(["Main"], FakeMenu, timeout=1)
        interaction = make_interaction()
        view.bind_to_interaction(interaction)

        await view.on_timeout()

        self.assertTrue(all(item.disabled for item in view.children))
        interaction.edit_original_response.assert_awaited_once_with(view=view)

    async def test_timeout_without_interaction_only_disables_items(self) -> None:
        view = NavView(["Main"], FakeMenu, timeout=1)

        await view.on_timeout()

        self.assertTrue(all(item.disabled for item in view.children))

    async def test_timeout_swallows_expired_token(self) -> None:
        view = NavView(["Main"], FakeMenu, timeout=1)
        interaction = make_interaction()
        interaction.edit_original_response.side_effect = make_http_error()
        view.bind_to_interaction(interaction)

        await view.on_timeout()  # must not raise

        interaction.edit_original_response.assert_awaited_once()

    async def test_interaction_check_remembers_latest_interaction(self) -> None:
        view = TimeoutView(timeout=1)
        first, second = make_interaction(), make_interaction()
        view.bind_to_interaction(first)

        allowed = await view.interaction_check(second)
        await view.on_timeout()

        self.assertTrue(allowed)
        second.edit_original_response.assert_awaited_once_with(view=view)
        first.edit_original_response.assert_not_awaited()


class PaginationViewTests(unittest.IsolatedAsyncioTestCase):
    def make_view(self, count: int = 3, **kwargs) -> PaginationView:
        embeds = [discord.Embed(title=f"Page {i}") for i in range(count)]
        return PaginationView(embeds, timeout=1, **kwargs)

    async def test_requires_at_least_one_embed(self) -> None:
        with self.assertRaises(ValueError):
            PaginationView([])

    async def test_initial_state_disables_backward_buttons(self) -> None:
        view = self.make_view()

        self.assertTrue(view.first.disabled)
        self.assertTrue(view.previous.disabled)
        self.assertFalse(view.next.disabled)
        self.assertFalse(view.last.disabled)
        self.assertEqual(view.current_page.label, "1/3")
        self.assertEqual(view.initial.title, "Page 0")

    async def test_initial_page_is_clamped(self) -> None:
        self.assertEqual(self.make_view(initial_page=99).initial.title, "Page 2")
        self.assertEqual(self.make_view(initial_page=-5).initial.title, "Page 0")

    async def test_next_and_previous_edit_message(self) -> None:
        view = self.make_view()
        interaction = make_interaction()

        await view.next.callback(interaction)
        kwargs = interaction.response.edit_message.await_args.kwargs
        self.assertEqual(kwargs["embed"].title, "Page 1")
        self.assertIs(kwargs["view"], view)
        self.assertEqual(view.current_page.label, "2/3")

        await view.previous.callback(interaction)
        self.assertEqual(
            interaction.response.edit_message.await_args.kwargs["embed"].title,
            "Page 0",
        )

    async def test_first_and_last_jump_to_edges(self) -> None:
        view = self.make_view(count=5)
        interaction = make_interaction()

        await view.last.callback(interaction)
        self.assertEqual(view.initial.title, "Page 4")
        self.assertTrue(view.next.disabled)
        self.assertTrue(view.last.disabled)

        await view.first.callback(interaction)
        self.assertEqual(view.initial.title, "Page 0")
        self.assertTrue(view.first.disabled)

    async def test_previous_on_first_page_does_nothing(self) -> None:
        view = self.make_view()
        interaction = make_interaction()

        await view.previous.callback(interaction)

        interaction.response.edit_message.assert_not_awaited()

    async def test_edit_failure_sends_ephemeral_error(self) -> None:
        view = self.make_view()
        interaction = make_interaction()
        interaction.response.edit_message.side_effect = RuntimeError("boom")

        await view.next.callback(interaction)

        interaction.response.send_message.assert_awaited_once()
        self.assertTrue(interaction.response.send_message.await_args.kwargs["ephemeral"])

    async def test_select_factory_is_rebuilt_for_every_page(self) -> None:
        pages_seen = []

        def factory(page: int) -> discord.ui.Select:
            pages_seen.append(page)
            return discord.ui.Select(options=[discord.SelectOption(label="x", value="x")])

        view = self.make_view(select_menu_factory=factory)
        await view.next.callback(make_interaction())

        self.assertEqual(pages_seen, [0, 1])
        self.assertEqual(
            len([item for item in view.children if isinstance(item, discord.ui.Select)]),
            1,
        )


class NavSelectTests(unittest.IsolatedAsyncioTestCase):
    def make_select(self, history, embed_cls=FakeMenu, **kwargs) -> NavSelect:
        return NavSelect(history, embed_cls, "Pick...", **kwargs)

    async def test_root_level_has_no_back_option(self) -> None:
        select = self.make_select(["Main"])

        self.assertEqual([option.value for option in select.options], ["Sub", "Other"])

    async def test_nested_level_adds_back_option(self) -> None:
        select = self.make_select(["Main", "Sub"])

        self.assertEqual(
            [option.value for option in select.options], ["Leaf", BACK_OPTION_VALUE]
        )

    async def test_choosing_child_opens_next_level(self) -> None:
        select = self.make_select(["Main"])
        select._values = ["Sub"]
        interaction = make_interaction()

        await select.callback(interaction)

        kwargs = interaction.response.edit_message.await_args.kwargs
        self.assertEqual(kwargs["embed"].title, "Sub")
        self.assertIsInstance(kwargs["view"], NavView)
        self.assertEqual(kwargs["view"].children[0].history, ["Main", "Sub"])

    async def test_back_returns_to_parent_level(self) -> None:
        select = self.make_select(["Main", "Sub"])
        select._values = [BACK_OPTION_VALUE]
        interaction = make_interaction()

        await select.callback(interaction)

        kwargs = interaction.response.edit_message.await_args.kwargs
        self.assertEqual(kwargs["embed"].title, "Main")
        self.assertEqual(kwargs["view"].children[0].history, ["Main"])

    async def test_new_view_is_bound_to_the_clicked_interaction(self) -> None:
        select = self.make_select(["Main"])
        select._values = ["Sub"]
        interaction = make_interaction()

        await select.callback(interaction)

        new_view = interaction.response.edit_message.await_args.kwargs["view"]
        await new_view.on_timeout()
        interaction.edit_original_response.assert_awaited_once_with(view=new_view)

    async def test_previous_view_is_stopped_after_navigation(self) -> None:
        view = NavView(["Main"], FakeMenu, timeout=1)
        select = view.children[0]
        select._values = ["Sub"]

        await select.callback(make_interaction())

        self.assertTrue(view.is_finished())

    async def test_option_page_is_clamped(self) -> None:
        select = self.make_select(["Main"], option_page=99)

        self.assertEqual(len(select.options), 2)


class NavigationLevelTests(unittest.IsolatedAsyncioTestCase):
    async def test_plain_level_builds_nav_view(self) -> None:
        embed, view = build_navigation_level(["Main"], FakeMenu, "Pick...", {})

        self.assertEqual(embed.title, "Main")
        self.assertIsInstance(view, NavView)

    async def test_many_children_use_paginated_select(self) -> None:
        page_state: dict = {}
        embed, view = build_navigation_level(["Main"], BigMenu, "Pick...", page_state)

        self.assertIsInstance(view, PaginationView)
        self.assertEqual(embed.title, "Items 1-25")
        select = next(i for i in view.children if isinstance(i, discord.ui.Select))
        self.assertEqual(len(select.options), MAX_SELECT_OPTIONS)

    async def test_page_state_follows_pagination_and_is_restored(self) -> None:
        page_state: dict = {}
        _, view = build_navigation_level(["Main"], BigMenu, "Pick...", page_state)

        await view.next.callback(make_interaction())

        self.assertEqual(page_state["Main"], 1)
        select = next(i for i in view.children if isinstance(i, discord.ui.Select))
        self.assertEqual(
            [option.value for option in select.options],
            [f"Item{i}" for i in range(25, 30)],
        )

        embed, restored = build_navigation_level(["Main"], BigMenu, "Pick...", page_state)
        self.assertEqual(embed.title, "Items 26-30")
        restored_select = next(
            i for i in restored.children if isinstance(i, discord.ui.Select)
        )
        self.assertEqual(
            [option.value for option in restored_select.options],
            [option.value for option in select.options],
        )

    async def test_page_count_mismatch_raises(self) -> None:
        class BrokenMenu(BigMenu):
            Main_pages = [discord.Embed(title="only one")]

        with self.assertRaises(ValueError):
            build_navigation_level(["Main"], BrokenMenu, "Pick...", {})


if __name__ == "__main__":
    unittest.main()
