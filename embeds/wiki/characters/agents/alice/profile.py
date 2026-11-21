"""Alice: profile section (lore and other non-combat information)."""

from embeds.wiki.characters.sections import section

from .common import placeholder_page

SECTION = section(
    key="AliceProfile",
    label="Профіль",
    summary="Історія та дані",
    pages=(
        placeholder_page("Біографія", "коротка біографія без великих сюжетних спойлерів"),
        placeholder_page(
            "Особисті дані",
            "повне ім'я, день народження, зріст, фракція та інші відомі дані",
        ),
        placeholder_page(
            "Озвучення та костюми",
            "актори озвучення (китайська, англійська, японська, корейська) і костюми",
        ),
        placeholder_page(
            "Медіа",
            "посилання на офіційні відео та сторінки агента",
        ),
    ),
)
