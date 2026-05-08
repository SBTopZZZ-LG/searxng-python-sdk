"""Custom HTTP URL type with protocol-relative URL normalization."""

from typing import Annotated

import pydantic
from pydantic import BeforeValidator, TypeAdapter

_http_url_adapter = TypeAdapter(pydantic.HttpUrl)


def _normalize_url(v: str) -> str:
    if isinstance(v, str) and v.startswith("//"):
        v = "https:" + v
    return str(_http_url_adapter.validate_python(v))


HttpUrl = Annotated[str, BeforeValidator(_normalize_url)]
