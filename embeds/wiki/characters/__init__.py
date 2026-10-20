"""Character command embeds and navigation registry."""

from .menu import CharactersMainEmbeds
from .routes import (
    AGENT_ROUTES,
    AgentRoute,
    find_agent_route,
    search_agent_routes,
)

__all__ = [
    "AGENT_ROUTES",
    "AgentRoute",
    "CharactersMainEmbeds",
    "find_agent_route",
    "search_agent_routes",
]
