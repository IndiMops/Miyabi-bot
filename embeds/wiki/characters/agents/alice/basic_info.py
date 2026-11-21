"""Alice: basic info section (overview and stats)."""

import discord

from embeds.general import add_fields
from embeds.wiki.characters.sections import section
from utils.misc import HEXtoColor

from .common import COLOR, decorate


# Page 1: overview.
OVERVIEW = discord.Embed(
    title="Огляд",
    description="Alice Thymefield — спадкоємиця престижної родини Thymefield, талановита фехтувальниця та дослідниця Ether science. Вона навчається у Celestia School for Girls, є зразковою ученицею та входить до складу Spook Shack.\n\nПопри сильний страх перед привидами й надприродними явищами, Alice відчуває до них майже нездорову цікавість. У бою вона виступає як Physical Anomaly DPS, накопичує ресурс Blade Etiquette та витрачає його на заряджену атаку Starshine Waltz, здатну активувати особливий ефект Polarized Assault.",
    color=HEXtoColor(COLOR),
).set_image(
    url="https://i.imgur.com/2Hf0bg6.png"
)

add_fields(OVERVIEW, [
    {
        "name": "Ранг:",
        "value": "<:Icon_AgentRank_S:1530870923085742111>",
        "inline": True,
    },
    {
        "name": "Атрибут:",
        "value": "<:Icon_Physical:1422213096117764116> Фізичний",
        "inline": True,
    },
    {
        "name": "Спеціалізація:",
        "value": "<:Icon_Anomaly:1530871749804036136> Аномалія",
        "inline": True,
    },
    {
        "name": "Фракція:",
        "value": "<:Faction_Spook_Shack:1530872488047804486> Spook Shack",
        "inline": True,
    },
    {"name": "Тип атаки:", "value": "Slash", "inline": True},
    {"name": "Бойова роль:", "value": "Anomaly DPS", "inline": True},
    {"name": "Реліз:", "value": "<t:1754484720:D> (версія 2.1)", "inline": True},
    {
        "name": "Отримання:",
        "value": "Лімітований агент, Exclusive Channel «Sworn to Noble Courage»",
        "inline": True,
    },
    {
        "name": "Ексклюзивний W-Engine:",
        "value": "<:Practiced_Perfection:1533459749700636673> [Відточена досконалість](https://zenless-zone-zero.fandom.com/wiki/Practiced_Perfection)",
        "inline": True,
    },
])

decorate(OVERVIEW)


# Page 2: stats.
STATS = discord.Embed(
    title="Характеристики",
    description="*Характеристики на 60 рівні з повністю відкритим Core Skill F, без W-Engine і Drive Discs.*\n\n",
    color=HEXtoColor(COLOR)
).set_image(
    url="https://i.imgur.com/4kwWaeR.png"
)

add_fields(STATS, [
    {
        "name": "⠀",
        "value": "- HP: 7 673\n- ATK: 880\n- DEF: 606\n- Impact: 86\n- CRIT Rate: 5%\n- CRIT DMG: 50%",
        "inline": True
    },
    {
        "name": "⠀",
        "value": "- Anomaly Mastery: 142\n- Anomaly Proficiency: 118\n- PEN Ratio: 0%\n- Energy Regen: 1,2",
        "inline": True
    },
    {
        "name": "Технічна примітка",
        "value": "Без бонусів Core Skill її базові характеристики на 60 рівні становлять приблизно:\n- Base ATK: 805,7\n- Anomaly Mastery: 106\n\nCore Skill F сумарно надає:\n- +75 Base ATK\n- +36 Anomaly Mastery.\n\n*Саме тому в одних базах можна побачити 806 ATK і 106 AM, а в інших 880 ATK і 142 AM. Просто одна показує чистий рівень, а інша враховує Core Skill.*",
        "inline": False
    }
])

decorate(STATS)


SECTION = section(
    key="AliceBasicInfo",
    label="Основна інформація",
    summary="Огляд персонажа",
    pages=(OVERVIEW, STATS),
)
