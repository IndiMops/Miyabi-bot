"""Alice: profile section (placeholder pages until the content is written)."""

from embeds.wiki.characters.sections import Section

from .common import placeholder_pages

SECTION = Section(
    key="AliceProfile",
    label="Профіль",
    summary="Історія та дані",
    pages=tuple(placeholder_pages("Профіль", 4)),
)
