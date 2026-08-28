"""Verified RO App API contract metadata used by MARSEL audit tooling.

Only facts already verified by official RO App documentation are represented
here. Unverified endpoints must not be added until independently confirmed.
"""

ROAPP_API_PAGE_SIZE = 50
ROAPP_API_RATE_LIMIT_PER_SECOND = 3
ROAPP_API_BASE_URL = "https://api.roapp.io/v2"

VERIFIED_READ_ENDPOINTS: tuple[str, ...] = (
    "/contacts/people",
    "/orders",
)

BLOCKED_WRITE_METHODS: frozenset[str] = frozenset({
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
})

OFFICIAL_DOCS_URL = "https://roapp.readme.io/reference/getting-started-with-api"
VERIFIED_PEOPLE_DOCS_URL = "https://roappua.readme.io/reference/get-people"
