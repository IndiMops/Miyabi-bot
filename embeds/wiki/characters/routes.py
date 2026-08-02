"""Navigation routes and aliases for direct character lookup."""

from dataclasses import dataclass
import unicodedata


@dataclass(frozen=True, slots=True)
class AgentRoute:
    """A stable character key and its position in the navigation tree."""

    key: str
    display_name: str
    category_key: str
    aliases: tuple[str, ...] = ()

    @property
    def history(self) -> list[str]:
        return ["Main", self.category_key, self.key]

    @property
    def search_terms(self) -> tuple[str, ...]:
        return (self.key, self.display_name, *self.aliases)


ALICE_ROUTE = AgentRoute(
    key="Alice",
    display_name="Аліса Таймфілд",
    category_key="PhysicalCharacters",
    aliases=(
        "Аліса",
        "Alice",
        "Alice Thymefield",
        "Alisa",
        "Alisa Thymefield",
    ),
)

FIRE_PLACEHOLDER_ROUTES = tuple(
    AgentRoute(
        key=f"FireAgent{index:02d}",
        display_name=f"Вогняний агент {index:02d}",
        category_key="FireCharacters",
        aliases=(
            f"Вогняний агент {index}",
            f"Агент {index}",
            f"Fire agent {index}",
        ),
    )
    for index in range(1, 36)
)

AGENT_ROUTES = (ALICE_ROUTE, *FIRE_PLACEHOLDER_ROUTES)


def normalize_agent_query(value: str) -> str:
    """Normalize user input for case-insensitive alias matching."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def _build_route_index() -> dict[str, AgentRoute]:
    index: dict[str, AgentRoute] = {}

    for route in AGENT_ROUTES:
        for term in route.search_terms:
            normalized_term = normalize_agent_query(term)
            existing_route = index.get(normalized_term)

            if existing_route is not None and existing_route != route:
                raise ValueError(
                    f"Duplicate agent alias {term!r} for "
                    f"{existing_route.key} and {route.key}"
                )

            index[normalized_term] = route

    return index


_ROUTES_BY_TERM = _build_route_index()


def find_agent_route(query: str) -> AgentRoute | None:
    """Find a route by internal key, display name, or exact alias."""
    return _ROUTES_BY_TERM.get(normalize_agent_query(query))


def search_agent_routes(
    query: str,
    *,
    limit: int = 25,
) -> list[AgentRoute]:
    """Return unique autocomplete matches, prioritizing exact/prefix hits."""
    if limit <= 0:
        return []

    normalized_query = normalize_agent_query(query)
    if not normalized_query:
        return list(AGENT_ROUTES[:limit])

    matches: list[tuple[int, str, AgentRoute]] = []

    for route in AGENT_ROUTES:
        terms = tuple(
            normalize_agent_query(term)
            for term in route.search_terms
        )

        if normalized_query in terms:
            score = 0
        elif any(term.startswith(normalized_query) for term in terms):
            score = 1
        elif any(normalized_query in term for term in terms):
            score = 2
        else:
            continue

        matches.append((score, route.display_name.casefold(), route))

    matches.sort(key=lambda match: (match[0], match[1]))
    return [route for _, _, route in matches[:limit]]
