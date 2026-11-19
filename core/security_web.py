from dataclasses import dataclass

from fastapi import HTTPException


@dataclass(frozen=True)
class WebContext:
    user_id: str
    scopes: frozenset[str]


def get_web_context() -> WebContext:
    raise HTTPException(status_code=401, detail="Authentication is required")


def require_scope(context: WebContext, scope: str) -> None:
    if scope not in context.scopes:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
