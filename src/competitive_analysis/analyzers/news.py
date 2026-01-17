"""News monitoring analyzer for competitor mentions."""

import re
from datetime import datetime
from urllib.parse import quote_plus
from xml.etree import ElementTree

from ..models import Competitor, NewsAnalysisResult, NewsItem
from .base import BaseAnalyzer


class NewsAnalyzer(BaseAnalyzer):
    """Monitor news mentions of competitors via Google News RSS."""

    @property
    def name(self) -> str:
        return "news"

    async def analyze(self, competitor: Competitor) -> NewsAnalysisResult:
        """Search for news mentions of a competitor."""
        # Use Google News RSS feed for the competitor name
        search_query = quote_plus(competitor.name)
        rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"

        try:
            response = await self.fetch_url(rss_url)
            items = self._parse_rss(response.text)
            return NewsAnalysisResult(
                items=items[:20],  # Limit to 20 most recent
                total_mentions=len(items),
            )
        except Exception:
            # Return empty result if RSS fetch fails
            return NewsAnalysisResult()

    def _parse_rss(self, xml_content: str) -> list[NewsItem]:
        """Parse RSS feed XML into NewsItem objects."""
        items = []
        try:
            root = ElementTree.fromstring(xml_content)
            channel = root.find("channel")
            if channel is None:
                return items

            for item in channel.findall("item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_date_elem = item.find("pubDate")
                source_elem = item.find("source")

                if title_elem is None or link_elem is None:
                    continue

                title = title_elem.text or ""
                url = link_elem.text or ""

                # Parse publication date
                published_at = None
                if pub_date_elem is not None and pub_date_elem.text:
                    published_at = self._parse_date(pub_date_elem.text)

                # Get source
                source = None
                if source_elem is not None:
                    source = source_elem.text

                # Extract snippet from description if available
                desc_elem = item.find("description")
                snippet = None
                if desc_elem is not None and desc_elem.text:
                    # Clean HTML from description
                    snippet = re.sub(r"<[^>]+>", "", desc_elem.text)[:200]

                items.append(
                    NewsItem(
                        title=title,
                        url=url,
                        source=source,
                        published_at=published_at,
                        snippet=snippet,
                    )
                )
        except ElementTree.ParseError:
            pass

        return items

    def _parse_date(self, date_str: str) -> datetime | None:
        """Parse RSS date format."""
        formats = [
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S%z",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
