from fastmcp import Context
import os

async def auth_unlock(ctx: Context, token: str) -> str:
    """Unlock dangerous tools for this session."""
    # Check against environment variable (default for dev: let_me_in)
    expected_token = os.getenv("COLDQUERY_AUTH_TOKEN", "let_me_in")

    if token == expected_token:
        ctx.session["unlocked"] = True
        return "Session unlocked. Dangerous tools enabled."
    return "Invalid token."
