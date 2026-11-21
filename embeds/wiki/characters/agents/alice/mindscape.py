"""Alice: Mindscape Cinema section, two Mindscapes per page.

Source: the Mindscape Cinema section of Alice's Fandom page.
"""

from embeds.wiki.characters.sections import section

from .common import field, page

SKILL_LEVELS = "Підвищує рівень Basic Attack, Dodge, Assist, Special Attack та Chain Attack на 2."

M1_M2 = page(
    "M1–M2",
    "Кожен рівень Mindscape потребує 1 Agent Focus: Alice.",
    fields=(
        field(
            "M1 — Palmful of Cilantro",
            "Polarized Assault дає Alice 25 Blade Etiquette. Кожен Assault, який "
            "викликає Alice, знижує DEF цілі на 20% на 30 с.\n"
            "**Практичний вплив:** швидше повертає ресурс для наступного заряду III і "
            "посилює шкоду всього загону по цілі.",
        ),
        field(
            "M2 — Sage at the Sword's Tip",
            "Завершальний удар Ultimate: Starfall Finale теж запускає Polarized "
            "Assault. Assault DMG усього загону +15%, шкода Disorder по ворогах під "
            "Physical Anomaly +15%. На початку бою Alice одразу отримує 1 000 Decibels "
            "(в Investigation Zone — раз на 180 с).\n"
            "**Практичний вплив:** другий спосіб запускати Polarized Assault і "
            "швидший перший Ultimate.",
        ),
    ),
)

M3_M4 = page(
    "M3–M4",
    fields=(
        field("M3 — Symmetrism", SKILL_LEVELS),
        field(
            "M4 — Rosemary on Her Lips",
            "Alice ігнорує 10% Physical RES цілі. Посилений Basic Attack: Celestial "
            "Overture накопичує на 25% більше Physical Anomaly Buildup.\n"
            "**Практичний вплив:** більше шкоди та частіші Assault, а отже й більше "
            "Blade Etiquette.",
        ),
    ),
)

M5_M6 = page(
    "M5–M6",
    fields=(
        field("M5 — Passion for the Supernatural", SKILL_LEVELS),
        field(
            "M6 — A Heart of Thyme",
            "Після заряду III Starshine Waltz або Ultimate: Starfall Finale Alice на "
            "30 с входить у Victory State. Поки він діє, влучання будь-кого із загону "
            "по цілі викликає додаткову атаку Alice: Physical DMG у 3 300% від її "
            "Anomaly Proficiency, гарантований CRIT, не частіше ніж раз на 1 с і до "
            "6 разів (новий Victory State оновлює лічильник).\n"
            "**Практичний вплив:** велике посилення в парі з союзниками, що часто б'ють.",
        ),
    ),
)

SECTION = section(
    key="AliceMindscapeCinema",
    label="Mindscape Cinema",
    summary="Рівні Mindscape",
    pages=(M1_M2, M3_M4, M5_M6),
)
