"""Alice: combat mechanics section (how her kit works together)."""

import discord

from embeds.general import add_fields
from embeds.wiki.characters.sections import Section
from utils.misc import HEXtoColor

from .common import COLOR, decorate


# Page 1: play style.
PLAY_STYLE = discord.Embed(
    title="Бойові механіки: Стиль гри",
    description="Alice є активним Anomaly DPS, ігровий процес якого обертається навколо трьох елементів:",
    color=HEXtoColor(COLOR)
).set_image(
    url="https://i.imgur.com/R1YEorB.png"
)

add_fields(PLAY_STYLE, [
    {
        "name": "Blade Etiquette",
        "value": "Унікальний ресурс Alice, потрібний для зарядженої Базових атак.",
        "inline": False
    },
    {
        "name": "Starshine Waltz",
        "value": "Потужна заряджена атака, що витрачає від однієї до трьох смуг Blade Etiquette.",
        "inline": False
    },
    {
        "name": "Polarity Assault",
        "value": "Особливий Assault, який не потребує повторного заповнення шкали Physical Anomaly та може викликати Disorder навіть разом з іншим Physical Anomaly.",
        "inline": False
    },
    {
        "name": "Спрощений бойовий цикл:",
        "value": (
            "1. Накопичити Blade Etiquette атаками та активаціями аномалій.\n"
            "2. Викликати Assault і Disorder.\n"
            "3. Накопичити 300 Blade Etiquette.\n"
            "4. Використати повністю заряджену Starshine Waltz.\n"
            "5. Активувати Polarity Assault.\n"
            "6. Використати Ultimate для відновлення 200 Blade Etiquette.\n"
            "7. Повторити цикл."
        ),
        "inline": False
    },
    {
        "name": "Примітка",
        'value': "*Найкраще використовувати Starshine Waltz із повним зарядом у три смуги. Використання однієї чи двох смуг можливе, але не активує головну частину її механіки — Polarity Assault.*",
        "inline": False
    }
])
decorate(PLAY_STYLE)


SECTION = Section(
    key="AliceCombatMechanics",
    label="Бойові механіки",
    summary="Особливості бою",
    pages=(PLAY_STYLE,),
)
