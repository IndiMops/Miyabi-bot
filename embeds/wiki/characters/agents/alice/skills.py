"""Alice: skills section, one page per standard ZZZ skill category."""

from embeds.wiki.characters.sections import section

from .common import placeholder_page

SECTION = section(
    key="AliceSkills",
    label="Навички",
    summary="Набір навичок",
    pages=(
        placeholder_page(
            "Basic Attack",
            "опис Basic Attack, ключова механіка та головні множники на Lv.12",
        ),
        placeholder_page(
            "Dodge",
            "Dodge, Dash Attack і Dodge Counter, їхні особливості та головні множники",
        ),
        placeholder_page(
            "Assist",
            "Quick Assist, Defensive/Evasive Assist і Assist Follow-Up та їхні множники",
        ),
        placeholder_page(
            "Special Attack",
            "Special Attack і EX Special Attack, вартість Energy та головні множники",
        ),
        placeholder_page(
            "Chain Attack / Ultimate",
            "Chain Attack і Ultimate, їхні ефекти та головні множники",
        ),
        placeholder_page(
            "Core Skill",
            "Core Passive, Additional Ability з умовою активації та бонуси Core Skill F",
        ),
    ),
)
