"""Alice: skills section (placeholder pages until the content is written)."""

from embeds.wiki.characters.sections import Section

from .common import placeholder_pages

SECTION = Section(
    key="AliceSkills",
    label="Навички",
    summary="Набір навичок",
    pages=tuple(placeholder_pages("Навички", 6)),
)
