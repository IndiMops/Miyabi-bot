"""Alice: progression section (placeholder pages until the content is written)."""

from embeds.wiki.characters.sections import Section

from .common import placeholder_pages

SECTION = Section(
    key="AliceProgression",
    label="Прокачування",
    summary="Матеріали й розвиток",
    pages=tuple(placeholder_pages("Прокачування", 4)),
)
