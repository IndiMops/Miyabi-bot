"""Navigation embeds and placeholder pages for Alice Thymefield."""

from typing import List

import discord

from embeds.general import add_default_footer, add_fields
from utils.misc import HEXtoColor

ALICE_COLOR = "243A63"
ALICE_ICON_URL = (
    "https://res.cloudinary.com/z5ozewii/image/upload/"
    "v1785057256/Agent_Alice_Thymefield_Icon_ojp90y.png"
)
ALICE_AUTHOR_ICON_URL = (
    "https://res.cloudinary.com/z5ozewii/image/upload/"
    "v1785055164/Message_Alice_Thymefield_Icon_webp_vr2vav.png"
)


def _decorate_alice_embed(embed: discord.Embed) -> discord.Embed:
    """Apply the shared Alice author, thumbnail, and project footer."""
    embed.set_author(
        name="Аліса Таймфілд",
        icon_url=ALICE_AUTHOR_ICON_URL,
        url="https://zenless-zone-zero.fandom.com/wiki/Alice_Thymefield",
    )
    embed.set_thumbnail(url=ALICE_ICON_URL)
    return add_default_footer(embed)


def _build_placeholder_pages(
    section_title: str,
    page_count: int,
) -> list[discord.Embed]:
    """Create temporary paginated embeds for an Alice information section."""
    return [
        _decorate_alice_embed(
            discord.Embed(
                title=f"{section_title} — {page}/{page_count}",
                description=(
                    f"Заглушка для сторінки {page} розділу "
                    f"«{section_title}». Тут пізніше буде додано вміст."
                ),
                color=HEXtoColor(ALICE_COLOR),
            )
        )
        for page in range(1, page_count + 1)
    ]


class AliceEmbed:
    Main_placeholder = "Оберіть розділ про Алісу..."
    Main_children = [
        {
            "label": "Основна інформація",
            "value": "AliceBasicInfo",
            "description": "Огляд персонажа — 2 сторінки",
        },
        {
            "label": "Бойові механіки",
            "value": "AliceCombatMechanics",
            "description": "Особливості бою — 3 сторінки",
        },
        {
            "label": "Навички",
            "value": "AliceSkills",
            "description": "Набір навичок — 6 сторінок",
        },
        {
            "label": "Mindscape Cinema",
            "value": "AliceMindscapeCinema",
            "description": "Рівні Mindscape — 3 сторінки",
        },
        {
            "label": "Прокачування",
            "value": "AliceProgression",
            "description": "Матеріали й розвиток — 4 сторінки",
        },
        {
            "label": "Профіль",
            "value": "AliceProfile",
            "description": "Історія та дані — 4 сторінки",
        },
    ]
    

    BasicInfoP1 = discord.Embed(
        title="Основна інформація: Огляд — 1/2",
        description="Alice Thymefield — спадкоємиця престижної родини Thymefield, талановита фехтувальниця та дослідниця Ether science. Вона навчається у Celestia School for Girls, є зразковою ученицею та входить до складу Spook Shack.\n\nПопри сильний страх перед привидами й надприродними явищами, Alice відчуває до них майже нездорову цікавість. У бою вона виступає як Physical Anomaly DPS, накопичує ресурс Blade Etiquette та витрачає його на заряджену атаку Starshine Waltz, здатну активувати особливий ефект Polarity Assault.",
        color=HEXtoColor(ALICE_COLOR),
    ).set_image(
        url="https://i.imgur.com/2Hf0bg6.png"
    )

    fields = [
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
        {"name": "Дата народження:", "value": "30.07", "inline": True},
        {"name": "Реліз:", "value": "<t:1754484720:D>", "inline": True},
        {
            "name": "Ексклюзивний W-Engine:",
            "value": "<:Practiced_Perfection:1533459749700636673> [Відточена досконалість](https://zenless-zone-zero.fandom.com/wiki/Practiced_Perfection)",
            "inline": True,
        },
    ]

    add_fields(BasicInfoP1, fields)
        
    _decorate_alice_embed(BasicInfoP1)
    
    
    # Second page of the Basic Info section is a placeholder for future content.
    BasicInfoP2 = discord.Embed(
        title="Основна інформація: Характеристики — 2/2",
        description="*Характеристики на 60 рівні з повністю відкритим Core Skill F, без W-Engine і Drive Discs.*\n\n",
        color=HEXtoColor(ALICE_COLOR)
    ).set_image(
        url="https://i.imgur.com/4kwWaeR.png"
    )
    
    fields = [
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
    ]
    add_fields(BasicInfoP2, fields)
    
    _decorate_alice_embed(BasicInfoP2)


    # Second menu "Battle Mechanics"
    BattleMechanicsP1 = discord.Embed(
        title="Бойові механіки: Стиль гри — 1/3",
        description="Alice є активним Anomaly DPS, ігровий процес якого обертається навколо трьох елементів:",
        color=HEXtoColor(ALICE_COLOR)
    ).set_image(
        url="https://i.imgur.com/R1YEorB.png"
    )
    
    fields = [
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
    ]

    add_fields(BattleMechanicsP1, fields)
    _decorate_alice_embed(BattleMechanicsP1)
    
    AliceBasicInfo_pages = [
        BasicInfoP1,
        BasicInfoP2,
    ]
    
    AliceCombatMechanics_pages = [
        BattleMechanicsP1
    ]
    AliceSkills_pages = _build_placeholder_pages("Навички", 6)
    AliceMindscapeCinema_pages = _build_placeholder_pages("Mindscape Cinema", 3)
    AliceProgression_pages = _build_placeholder_pages("Прокачування", 4)
    AliceProfile_pages = _build_placeholder_pages("Профіль", 4)

    # Entering Alice immediately opens the first information section while
    # keeping all character tabs available in the select menu.
    Main = AliceBasicInfo_pages[0]
    Main_pages = AliceBasicInfo_pages

    # A regular embed is kept for the navigation contract; pagination uses the
    # corresponding ``<key>_pages`` list when a section is selected.
    AliceBasicInfo = AliceBasicInfo_pages[0]
    AliceCombatMechanics = AliceCombatMechanics_pages[0]
    AliceSkills = AliceSkills_pages[0]
    AliceMindscapeCinema = AliceMindscapeCinema_pages[0]
    AliceProgression = AliceProgression_pages[0]
    AliceProfile = AliceProfile_pages[0]

    @classmethod
    def get_embed(cls, key: str) -> discord.Embed:
        return getattr(cls, key)

    @classmethod
    def get_children(cls, key: str) -> List[str]:
        return getattr(cls, f"{key}_children", [])

    @classmethod
    def get_pages(cls, key: str):
        return getattr(cls, f"{key}_pages", None)

    @classmethod
    def get_placeholder(cls, key: str, fallback: str) -> str:
        return getattr(cls, f"{key}_placeholder", fallback)
