"""
Rate-limiting setup using slowapi (wraps the `limits` library).

Limiter is created once here and imported wherever needed.
The default key function uses the client's real IP address.

Usage in a router:
    from core.middleware.rate_limit import limiter
    from slowapi.util import get_remote_address

    @router.post("/login")
    @limiter.limit("10/minute")
    async def login(request: Request, ...):
        ...
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
