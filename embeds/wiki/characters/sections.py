"""Shared building blocks for agent pages (see docs/agent-template.md)."""

from collections.abc import Sequence
from dataclasses import dataclass

import discord


def pages_label(count: int) -> str:
    """Return "N сторінка/сторінки/сторінок" with the right Ukrainian plural."""
    last_two_digits = count % 100
    last_digit = count % 10
    if last_digit == 1 and last_two_digits != 11:
        word = "сторінка"
    elif 2 <= last_digit <= 4 and not 12 <= last_two_digits <= 14:
        word = "сторінки"
    else:
        word = "сторінок"
    return f"{count} {word}"


@dataclass(frozen=True)
class Section:
    """One section of an agent: a select-menu tab with its paginated pages."""

    key: str
    label: str
    summary: str
    pages: tuple[discord.Embed, ...]

    def __post_init__(self) -> None:
        if not self.pages:
            raise ValueError(f"Section {self.key} needs at least one page")

    @property
    def tab(self) -> dict[str, str]:
        """Select option of the section; the page count is always the real one."""
        return {
            "label": self.label,
            "value": self.key,
            "description": f"{self.summary} — {pages_label(len(self.pages))}",
        }


def section(
    key: str,
    label: str,
    summary: str,
    pages: Sequence[discord.Embed],
) -> Section:
    """Create a section and give each page its full title.

    Pages are created with a short page name as the title ("Огляд"); here it
    becomes "<label>: <page name> — <index>/<count>". The number is added only
    when the section has more than one page, so it can never drift from the
    real page count.
    """
    count = len(pages)
    for index, page in enumerate(pages, start=1):
        number = f" — {index}/{count}" if count > 1 else ""
        page.title = f"{label}: {page.title}{number}"
    return Section(key=key, label=label, summary=summary, pages=tuple(pages))
