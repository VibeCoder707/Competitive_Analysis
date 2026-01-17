"""Base analyzer class with async support and rate limiting."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import httpx

from ..config import load_config
from ..models import Competitor

T = TypeVar("T")


class BaseAnalyzer(ABC):
    """Base class for all analyzers."""

    def __init__(self) -> None:
        self._config = load_config()
        self._last_request_time: float = 0

    async def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        delay = self._config.rate_limit_delay
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - self._last_request_time
        if elapsed < delay:
            await asyncio.sleep(delay - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch_url(self, url: str, timeout: float = 30.0) -> httpx.Response:
        """Fetch a URL with rate limiting."""
        await self._rate_limit()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "CompetitiveAnalysis/0.1 (Research Tool)"
                },
            )
            response.raise_for_status()
            return response

    @abstractmethod
    async def analyze(self, competitor: Competitor) -> Any:
        """Run analysis on a competitor. Must be implemented by subclasses."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the analyzer name."""
        pass
