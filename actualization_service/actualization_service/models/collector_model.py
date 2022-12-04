from pydantic import HttpUrl, PositiveInt
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class CollectorResponse:
    """Response from collector."""

    status: PositiveInt
    page_content: str
    request_url: HttpUrl

    @property
    def last_part_url(self) -> str:
        return self.request_url.split("/")[-1]
