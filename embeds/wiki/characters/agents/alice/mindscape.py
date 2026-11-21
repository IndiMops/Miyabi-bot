"""Alice: Mindscape Cinema section (placeholder pages until the content is written)."""

from embeds.wiki.characters.sections import Section

from .common import placeholder_pages

SECTION = Section(
    key="AliceMindscapeCinema",
    label="Mindscape Cinema",
    summary="Рівні Mindscape",
    pages=tuple(placeholder_pages("Mindscape Cinema", 3)),
)
