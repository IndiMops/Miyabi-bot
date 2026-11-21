"""Alice: profile section (lore and other non-combat information).

Sources: Alice's Fandom pages (infobox, Lore, Fashion, Media); the video links
are the official Zenless Zone Zero YouTube channel (checked via oEmbed), the
HoYoLAB link is the official Agent Record post. Big story spoilers are left out.
"""

from embeds.wiki.characters.sections import section

from .common import field, page

BIOGRAPHY = page(
    "Біографія",
    "Alice Thymefield — молода спадкоємиця Thymefield, однієї з найстаріших "
    "шляхетних родин New Eridu, відомої дослідженнями в Ether science. Змалку "
    "вона вивчає фехтування та Ether science і в обох має винятковий талант. "
    "Зараз Alice навчається в Celestia School for Girls (філія High Ambitions "
    "Academy) і вважається зразковою ученицею.\n\n"
    "Вона надзвичайно цінує порядок і понад усе — симетрію: саме за нею Alice "
    "вирішує, що красиве, а що ні. Привиди й моторошні історії лякають її до "
    "тремтіння, але цікавість щоразу перемагає.\n\n"
    "Батьки Alice рано пішли з життя, дідусь тяжко хворіє, тож вона прагне "
    "власними силами відродити родину. Попри боязкість, задуману справу вона "
    "доводить до кінця й ніколи не лишає друзів у біді. До Spook Shack, форуму "
    "Inter-Knot, де розгадують таємниці, її привела Ukinami Yuzuha.",
)

PERSONAL_DATA = page(
    "Особисті дані",
    fields=(
        field("Повне ім'я", "Alice Thymefield", inline=True),
        field("Стать", "Жіноча", inline=True),
        field("Вид", "Thiren (кролик)", inline=True),
        field("Зріст", "163 см (з вухами)", inline=True),
        field("День народження", "30 серпня", inline=True),
        field("Фракція", "Spook Shack", inline=True),
        field("Навчання", "Celestia School for Girls", inline=True),
        field("Спеціалізація", "Фехтування, Ether science", inline=True),
        field(
            "Родина",
            "Родина Thymefield: батько Lionel Thymefield і мати (обоє померли), дідусь",
            inline=True,
        ),
    ),
)

VOICE_AND_OUTFITS = page(
    "Озвучення та костюми",
    fields=(
        field("Китайська", "Duoduo (多多)", inline=True),
        field("Англійська", "Diana Garnet", inline=True),
        field("Японська", "Minami Tanaka (田中美海)", inline=True),
        field("Корейська", "Park Shi-yoon (박시윤)", inline=True),
        field(
            "Костюми",
            "**Celestian Etiquette** — стандартний.\n"
            "**Sea of Thyme** — платний S-костюм з Today's Outfit "
            "([відео](https://www.youtube.com/watch?v=Veo34JyRIj4)).",
        ),
    ),
)

MEDIA = page(
    "Медіа",
    "Офіційні відео й матеріали про Alice — кнопки під повідомленням.",
    fields=(
        field(
            "Відео Zenless Zone Zero",
            "**Agent Record** — коротке представлення агента.\n"
            "**Character Teaser** «A Lady's Tenet» — сюжетний ролик.\n"
            "**Character Demo** «Sword and Waltz» — демонстрація бою.\n"
            "**For Display Only** — короткий ролик з Alice.",
        ),
        field("HoYoLAB", "Офіційний пост Agent Record з представленням Alice."),
    ),
    links=(
        ("Agent Record", "https://www.youtube.com/watch?v=IUnJ0me5qPA"),
        ("Character Teaser", "https://www.youtube.com/watch?v=kBQnjxq8Fc8"),
        ("Character Demo", "https://www.youtube.com/watch?v=Fp7tFxXMoRM"),
        ("For Display Only", "https://www.youtube.com/watch?v=tXqB9eezMxo"),
        ("HoYoLAB", "https://www.hoyolab.com/article/39231485"),
    ),
)

SECTION = section(
    key="AliceProfile",
    label="Профіль",
    summary="Історія та дані",
    pages=(BIOGRAPHY, PERSONAL_DATA, VOICE_AND_OUTFITS, MEDIA),
)
