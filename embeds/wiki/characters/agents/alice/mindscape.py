"""Alice: Mindscape Cinema section, two Mindscapes per page."""

from embeds.wiki.characters.sections import section

from .common import placeholder_page

SECTION = section(
    key="AliceMindscapeCinema",
    label="Mindscape Cinema",
    summary="Рівні Mindscape",
    pages=(
        placeholder_page("M1–M2", "ефекти M1 і M2 та їхній практичний вплив на гру"),
        placeholder_page("M3–M4", "ефекти M3 і M4 та їхній практичний вплив на гру"),
        placeholder_page("M5–M6", "ефекти M5 і M6 та їхній практичний вплив на гру"),
    ),
)
