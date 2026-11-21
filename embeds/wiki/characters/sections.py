"""Shared building blocks for agent pages (see docs/agent-template.md)."""

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
