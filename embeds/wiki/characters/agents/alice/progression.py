"""Alice: progression section (materials needed to level her up)."""

from embeds.wiki.characters.sections import section

from .common import placeholder_page

SECTION = section(
    key="AliceProgression",
    label="Прокачування",
    summary="Матеріали й розвиток",
    pages=(
        placeholder_page("Рівень агента", "матеріали EXP і Denny для рівнів 1 → 60"),
        placeholder_page(
            "Promotion",
            "матеріали для підвищення рівневого ліміту з розподілом по рівнях",
        ),
        placeholder_page(
            "Навички та Core Skill",
            "матеріали для п'яти основних навичок і для Core Skill A → F",
        ),
        placeholder_page(
            "Загальна вартість",
            "усі матеріали для повного прокачування агента",
        ),
    ),
)
