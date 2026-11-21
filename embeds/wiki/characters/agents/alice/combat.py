"""Alice: combat mechanics section (how her kit works together).

Sources: Fandom skill pages of Alice (Core Passive, Additional Ability,
Starshine Waltz, Ultimate, EX Special Attack), multipliers at skill Lv.12.
"""

import discord

from embeds.general import add_fields
from embeds.wiki.characters.sections import section
from utils.misc import HEXtoColor

from .common import COLOR, decorate, field, page


# Page 1: play style.
PLAY_STYLE = discord.Embed(
    title="Стиль гри",
    description="Alice є активним Anomaly DPS, ігровий процес якого обертається навколо трьох елементів:",
    color=HEXtoColor(COLOR)
).set_image(
    url="https://i.imgur.com/R1YEorB.png"
)

add_fields(PLAY_STYLE, [
    {
        "name": "Blade Etiquette",
        "value": "Унікальний ресурс Alice (до 3 смуг), потрібний для зарядженої атаки Starshine Waltz.",
        "inline": False
    },
    {
        "name": "Starshine Waltz",
        "value": "Потужна заряджена атака, що витрачає від однієї до трьох смуг Blade Etiquette.",
        "inline": False
    },
    {
        "name": "Polarized Assault",
        "value": "Особливий Assault, який не потребує заповнення шкали Physical Anomaly та може викликати Disorder разом з будь-якою Attribute Anomaly, навіть з Physical.",
        "inline": False
    },
    {
        "name": "Спрощений бойовий цикл:",
        "value": (
            "1. Накопичити Blade Etiquette атаками та активаціями аномалій.\n"
            "2. Викликати Assault і Disorder.\n"
            "3. Накопичити 300 Blade Etiquette.\n"
            "4. Використати повністю заряджену Starshine Waltz.\n"
            "5. Завершальний удар запускає Polarized Assault, а з ним — Disorder.\n"
            "6. Використати Ultimate для відновлення 200 Blade Etiquette.\n"
            "7. Повторити цикл."
        ),
        "inline": False
    },
    {
        "name": "Примітка",
        'value': "*Найкраще використовувати Starshine Waltz із повним зарядом у три смуги. Використання однієї чи двох смуг можливе, але не активує головну частину її механіки — Polarized Assault.*",
        "inline": False
    }
])
decorate(PLAY_STYLE)


# Page 2: the resource and the attack that spends it.
BLADE_ETIQUETTE = page(
    "Blade Etiquette та Starshine Waltz",
    "Blade Etiquette — ресурс, який Alice накопичує в бою, а Starshine Waltz — "
    "заряджена атака, що його витрачає.",
    fields=(
        field("Запас", "Максимум **300** Blade Etiquette: 3 смуги по 100."),
        field(
            "Як накопичується",
            "- влучання атаками Alice;\n"
            "- +10 за кожен Assault, викликаний накопиченням Anomaly;\n"
            "- +10 за EX Special Attack: Aurora Thrust;\n"
            "- +200 за Ultimate: Starfall Finale;\n"
            "- +30 за кожен Disorder загону та +300 на початку бою, якщо в загоні є ще "
            "Anomaly або Support агент (Additional Ability; в Investigation Zone — раз на 180 с).\n"
            "Влучання самих Starshine Waltz і Ultimate ресурсу не дають.",
        ),
        field(
            "Як використати Starshine Waltz",
            "Коли є хоча б 1 смуга, затисніть Basic Attack: заряд витрачає до 3 смуг. "
            "Атака спрацьовує, щойно ви відпустите кнопку або коли залишиться менше "
            "1 смуги: серія ударів по області навколо цілі, кількість ударів залежить "
            "від заряду. Під час атаки Alice невразлива.",
        ),
        field("Рівні заряду (Lv.12)", "I — 378.1%\nII — 609.1%\nIII — 1931.5%", inline=True),
        field(
            "Чому чекати заряд III",
            "Він завдає приблизно в 5 разів більше шкоди, ніж заряд I, а його "
            "завершальний удар запускає Polarized Assault.",
            inline=True,
        ),
    ),
)


# Page 3: the special Assault and the Disorder it feeds.
POLARIZED_ASSAULT = page(
    "Polarized Assault і Disorder",
    "Polarized Assault — особливий Assault Alice, на якому тримається її шкода "
    "через Disorder.",
    fields=(
        field(
            "Як викликати",
            "Завершальний удар Starshine Waltz із зарядом III. З M2 — також "
            "завершальний удар Ultimate: Starfall Finale.",
        ),
        field(
            "Чим відрізняється від звичайного Assault",
            "- завдає 100% шкоди звичайного Assault;\n"
            "- не потребує накопичення шкали Physical Anomaly;\n"
            "- поєднується з будь-якою Attribute Anomaly на ворогові, навіть з "
            "Physical, і викликає Disorder.",
        ),
        field(
            "Бонус до Disorder",
            "Якщо Disorder спрацьовує, поки ворог під Physical Anomaly, за кожну "
            "секунду, що лишилася до її кінця, множник шкоди Disorder зростає на 18% "
            "(до +180%).",
        ),
        field(
            "Інші бонуси Core Passive",
            "- поки на ворогові діє Physical Anomaly будь-кого із загону, Alice кожні "
            "0.95 с завдає додаткову шкоду — 2.5% від шкоди цієї Anomaly;\n"
            "- кожен Assault на 30 с підвищує її Physical Anomaly Buildup Rate "
            "(до 25% на Core Skill F).",
        ),
        field(
            "Практичний вплив",
            "Що раніше після Physical Anomaly спрацює Disorder, то більший бонус: "
            "запускайте Polarized Assault, поки Physical Anomaly на ворогові ще свіжа.",
        ),
    ),
)


SECTION = section(
    key="AliceCombatMechanics",
    label="Бойові механіки",
    summary="Особливості бою",
    pages=(PLAY_STYLE, BLADE_ETIQUETTE, POLARIZED_ASSAULT),
)
