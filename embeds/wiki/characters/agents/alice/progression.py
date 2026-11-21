"""Alice: progression section (materials needed to level her up).

Sources: Fandom (Agent EXP Material, promotion and skill/core enhancement
tables); totals cross-checked with LootBar's Alice materials guide.
Leveling itself costs no Denny; W-Engine and Drive Discs are not included.
"""

from embeds.wiki.characters.sections import section

from .common import field, page

LEVEL = page(
    "Рівень агента",
    "Рівні 1 → 60 потребують **900 000 EXP**. Між рівнями 10, 20, 30, 40 і 50 "
    "потрібна Promotion (наступна сторінка).",
    fields=(
        field("Матеріали", "Senior Investigator Log ×300 (по 3 000 EXP)"),
        field(
            "За діапазонами",
            "1 → 10: ×2\n10 → 20: ×8\n20 → 30: ×20\n30 → 40: ×45\n40 → 50: ×75\n50 → 60: ×150",
        ),
    ),
)

PROMOTION = page(
    "Promotion",
    "Матеріали для підвищення рівневого ліміту (Anomaly Certification Seals).",
    fields=(
        field("Lv.10", "Basic Anomaly Certification Seal ×4\nDenny ×24 000", inline=True),
        field("Lv.20", "Advanced Anomaly Certification Seal ×12\nDenny ×56 000", inline=True),
        field("Lv.30", "Advanced Anomaly Certification Seal ×20\nDenny ×120 000", inline=True),
        field("Lv.40", "Controller Certification Seal ×10\nDenny ×200 000", inline=True),
        field("Lv.50", "Controller Certification Seal ×20\nDenny ×400 000", inline=True),
        field(
            "Разом",
            "Basic Anomaly Certification Seal ×4\n"
            "Advanced Anomaly Certification Seal ×32\n"
            "Controller Certification Seal ×30\n"
            "Denny ×800 000",
            inline=True,
        ),
    ),
)

SKILLS_AND_CORE = page(
    "Навички та Core Skill",
    "П'ять основних навичок: Basic Attack, Dodge, Assist, Special Attack, Chain Attack.",
    fields=(
        field(
            "Одна навичка 1 → 12",
            "Basic Physical Chip ×5\nAdvanced Physical Chip ×15\n"
            "Specialized Physical Chip ×50\nHamster Cage Pass ×1\nDenny ×500 000",
            inline=True,
        ),
        field(
            "Усі 5 навичок",
            "Basic Physical Chip ×25\nAdvanced Physical Chip ×75\n"
            "Specialized Physical Chip ×250\nHamster Cage Pass ×5\nDenny ×2 500 000",
            inline=True,
        ),
        field(
            "Core Skill до F",
            "Higher Dimensional Data: Toxic Edge ×60\nSycophant's Refinement ×9\n"
            "Denny ×405 000",
        ),
        field(
            "Core Skill за рівнями",
            "A (Lv.15): Denny ×5 000\n"
            "B (Lv.25): Toxic Edge ×2 · Denny ×12 000\n"
            "C (Lv.35): Toxic Edge ×4 · Denny ×28 000\n"
            "D (Lv.45): Toxic Edge ×9 · Sycophant's Refinement ×2 · Denny ×60 000\n"
            "E (Lv.55): Toxic Edge ×15 · Sycophant's Refinement ×3 · Denny ×100 000\n"
            "F (Lv.60): Toxic Edge ×30 · Sycophant's Refinement ×4 · Denny ×200 000",
        ),
    ),
)

TOTAL = page(
    "Загальна вартість",
    "Усе для рівня 60, усіх навичок 12 і Core Skill F (без W-Engine і Drive Discs).",
    fields=(
        field("EXP", "Senior Investigator Log ×300", inline=True),
        field(
            "Promotion",
            "Basic Anomaly Certification Seal ×4\n"
            "Advanced Anomaly Certification Seal ×32\n"
            "Controller Certification Seal ×30",
            inline=True,
        ),
        field(
            "Навички",
            "Basic Physical Chip ×25\nAdvanced Physical Chip ×75\n"
            "Specialized Physical Chip ×250\nHamster Cage Pass ×5",
            inline=True,
        ),
        field(
            "Core Skill",
            "Higher Dimensional Data: Toxic Edge ×60\nSycophant's Refinement ×9",
            inline=True,
        ),
        field(
            "Denny",
            "×3 705 000 (Promotion 800 000 + навички 2 500 000 + Core Skill 405 000)",
        ),
    ),
)

SECTION = section(
    key="AliceProgression",
    label="Прокачування",
    summary="Матеріали й розвиток",
    pages=(LEVEL, PROMOTION, SKILLS_AND_CORE, TOTAL),
)
