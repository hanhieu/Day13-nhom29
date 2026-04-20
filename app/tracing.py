from __future__ import annotations

import hashlib
import os
from contextlib import contextmanager
from typing import Any

try:
    from langfuse import get_client, propagate_attributes
    from langfuse.decorators import langfuse_context, observe
    _langfuse_client = get_client()
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    @contextmanager
    def propagate_attributes(**kwargs: Any):
        yield

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

        def update_current_span(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()
    _langfuse_client = None


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def trace_id_from_correlation_id(correlation_id: str) -> str:
    """Create a deterministic 32-char hex trace ID from correlation_id."""
    seed = (correlation_id or "").strip()
    if not seed:
        return ""

    if _langfuse_client is not None:
        try:
            return _langfuse_client.create_trace_id(seed=seed)
        except Exception:
            pass

    return hashlib.md5(seed.encode("utf-8")).hexdigest()


def get_current_trace_id() -> str | None:
    if _langfuse_client is None:
        return None
    try:
        return _langfuse_client.get_current_trace_id()
    except Exception:
        return None


def get_current_observation_id() -> str | None:
    if _langfuse_client is None:
        return None
    try:
        return _langfuse_client.get_current_observation_id()
    except Exception:
        return None
