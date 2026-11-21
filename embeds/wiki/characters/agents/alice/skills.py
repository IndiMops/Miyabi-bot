"""Alice: skills section, one page per standard ZZZ skill category.

Sources: Fandom skill pages of Alice; DMG multipliers at skill Lv.12
(Daze for Defensive Assist, which deals no DMG).
"""

from embeds.wiki.characters.sections import section

from .common import field, page

BASIC_ATTACK = page(
    "Basic Attack",
    "Звичайна серія ударів і заряджена атака за Blade Etiquette.",
    fields=(
        field(
            "Basic Attack: Celestial Overture",
            "До 5 ударів мечем уперед, Physical DMG.\n"
            "**Особливість:** після Assault, викликаного накопиченням Attribute "
            "Anomaly, 5-й удар наступної серії посилюється.\n"
            "**Lv.12:** 111.2% / 176% / 133.2% / 224.1% / 261.2%; посилений 5-й удар — 437.2%.",
        ),
        field(
            "Basic Attack: Starshine Waltz",
            "Заряджена атака, доступна від 1 смуги Blade Etiquette: затисніть Basic "
            "Attack, заряд витрачає до 3 смуг. Серія ударів по області навколо цілі, "
            "велика Physical DMG.\n"
            "**Особливість:** заряд III запускає Polarized Assault; влучання не дають "
            "Blade Etiquette; невразливість.\n"
            "**Lv.12:** заряд I — 378.1%, II — 609.1%, III — 1931.5%.\n"
            "*Докладніше — у «Бойових механіках».*",
        ),
    ),
)

DODGE = page(
    "Dodge",
    "Ухилення та атаки після нього.",
    fields=(
        field("Dodge: Jumpy Bunny", "Швидкий ривок-ухилення з невразливістю."),
        field(
            "Dash Attack: Blade-Dancer's Gale",
            "Basic Attack під час ухилення: удар мечем уперед, Physical DMG.\n"
            "**Lv.12:** 151.2%.",
        ),
        field(
            "Dodge Counter: Ceremony of Swordlight",
            "Basic Attack після Perfect Dodge: удар мечем і ногою по ворогах попереду, "
            "Physical DMG, невразливість.\n"
            "**Lv.12:** 568.9%.",
        ),
    ),
)

ASSIST = page(
    "Assist",
    "Alice має Defensive Assist: парирування замість ухилення.",
    fields=(
        field(
            "Quick Assist: Intertwined Stab",
            "Assist, коли активного персонажа підкинуто: удар мечем і ногою, "
            "Physical DMG, невразливість.\n"
            "**Lv.12:** 327.2%.",
        ),
        field(
            "Defensive Assist: Parry Guard",
            "Assist перед ударом ворога по активному персонажу: парирує атаку й "
            "завдає великого Daze, невразливість.\n"
            "**Lv.12 Daze:** Light — 366.3%, Heavy — 463.7%, Chain — 226.1%.",
        ),
        field(
            "Assist Follow-Up: Cross Riposte",
            "Basic Attack після Defensive Assist: ривок уперед з ударом мечем, "
            "Physical DMG, невразливість.\n"
            "**Lv.12:** 666%.",
        ),
    ),
)

SPECIAL_ATTACK = page(
    "Special Attack",
    "Обидва EX Special Attack коштують 40 Energy і дають +10 Blade Etiquette.",
    fields=(
        field(
            "Special Attack: Piercing Dawn",
            "Кидає клинок, що пробиває ворогів попереду, Physical DMG. Може "
            "викликати Perfect Dodge; після нього Basic Attack одразу робить 5-й "
            "удар серії. Невразливість.\n"
            "**Lv.12:** 125.1%.",
        ),
        field(
            "EX Special Attack: Aurora Thrust - Northern Cross",
            "Стік уперед + EX: випад крізь ворогів попереду, велика Physical DMG. "
            "Може викликати Perfect Dodge, невразливість.\n"
            "**Energy:** 40. **Lv.12:** 920.9%.",
        ),
        field(
            "EX Special Attack: Aurora Thrust - Southern Cross",
            "EX без руху стіка або зі стіком назад: відскок з ударом, потім випад "
            "уперед, Physical DMG. Може викликати Perfect Dodge, невразливість.\n"
            "**Energy:** 40. **Lv.12:** 1064.4%.",
        ),
    ),
)

CHAIN_ULTIMATE = page(
    "Chain Attack / Ultimate",
    "Найсильніші атаки Alice.",
    fields=(
        field(
            "Chain Attack: Starfall Intermission",
            "Серія потужних ударів по ворогах попереду, велика Physical DMG, "
            "невразливість.\n"
            "**Lv.12:** 1332.9%.",
        ),
        field(
            "Ultimate: Starfall Finale",
            "За максимального Decibel Rating: потужні удари по великій області "
            "попереду, велика Physical DMG, невразливість.\n"
            "**Особливість:** відновлює 200 Blade Etiquette (влучання ресурсу не "
            "дають); з M2 завершальний удар запускає Polarized Assault.\n"
            "**Lv.12:** 4524.7%.",
        ),
    ),
)

CORE_SKILL = page(
    "Core Skill",
    fields=(
        field(
            "Core Passive: Twin Rainbows of the Swordheart",
            "- поки на ворогові діє Physical Anomaly будь-кого із загону, Alice кожні "
            "0.95 с завдає додаткову шкоду — 2.5% від шкоди цієї Anomaly;\n"
            "- Disorder на ворогові під Physical Anomaly: +18% до множника шкоди "
            "Disorder за кожну секунду, що лишилася (до +180%);\n"
            "- атаки накопичують Blade Etiquette (максимум 300 = 3 смуги), +10 за "
            "Assault через накопичення Anomaly;\n"
            "- заряд III Starshine Waltz запускає Polarized Assault (100% шкоди Assault);\n"
            "- кожен Assault на 30 с підвищує Physical Anomaly Buildup Rate: від 12.5% "
            "до 25% на Core Skill F.",
        ),
        field(
            "Additional Ability: Mystery Hunt",
            "**Умова:** у загоні є ще Anomaly або Support агент.\n"
            "- +30 Blade Etiquette за кожен Disorder загону;\n"
            "- кожна одиниця Anomaly Mastery понад 140 дає 1.6 Anomaly Proficiency;\n"
            "- +300 Blade Etiquette на початку бою (в Investigation Zone — раз на 180 с).",
        ),
        field(
            "Бонуси Core Skill F",
            "+75 Base ATK і +36 Anomaly Mastery (тричі по +25 ATK і +12 AM).",
        ),
    ),
)

SECTION = section(
    key="AliceSkills",
    label="Навички",
    summary="Набір навичок",
    pages=(BASIC_ATTACK, DODGE, ASSIST, SPECIAL_ATTACK, CHAIN_ULTIMATE, CORE_SKILL),
)
