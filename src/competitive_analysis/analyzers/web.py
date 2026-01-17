"""Web scraping analyzer for competitor websites."""

import time

from bs4 import BeautifulSoup

from ..models import Competitor, WebAnalysisResult
from .base import BaseAnalyzer


class WebAnalyzer(BaseAnalyzer):
    """Analyze competitor websites via web scraping."""

    @property
    def name(self) -> str:
        return "web"

    async def analyze(self, competitor: Competitor) -> WebAnalysisResult | None:
        """Scrape and analyze a competitor's website."""
        if not competitor.url:
            return None

        start_time = time.monotonic()
        response = await self.fetch_url(str(competitor.url))
        load_time = (time.monotonic() - start_time) * 1000

        soup = BeautifulSoup(response.text, "lxml")

        # Extract title
        title = None
        if soup.title:
            title = soup.title.string

        # Extract meta description
        description = None
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"]

        # Extract headings
        headings = []
        for tag in ["h1", "h2", "h3"]:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text:
                    headings.append(f"{tag}: {text}")

        # Count links and images
        links_count = len(soup.find_all("a", href=True))
        images_count = len(soup.find_all("img"))

        # Detect technologies
        technologies = self._detect_technologies(soup, response.text)

        return WebAnalysisResult(
            title=title,
            description=description,
            headings=headings[:20],  # Limit to first 20
            links_count=links_count,
            images_count=images_count,
            technologies=technologies,
            page_size_bytes=len(response.content),
            load_time_ms=load_time,
        )

    def _detect_technologies(self, soup: BeautifulSoup, html: str) -> list[str]:
        """Detect web technologies used on the page."""
        technologies = []

        # Check for common frameworks/libraries
        tech_signatures = {
            "React": ["react", "_reactRootContainer", "data-reactroot"],
            "Vue.js": ["vue", "__vue__", "data-v-"],
            "Angular": ["ng-", "angular", "_ngcontent"],
            "jQuery": ["jquery", "jQuery"],
            "Bootstrap": ["bootstrap"],
            "Tailwind": ["tailwind"],
            "WordPress": ["wp-content", "wp-includes"],
            "Shopify": ["shopify", "cdn.shopify"],
            "Next.js": ["_next", "__NEXT_DATA__"],
            "Gatsby": ["gatsby"],
        }

        html_lower = html.lower()
        for tech, signatures in tech_signatures.items():
            for sig in signatures:
                if sig.lower() in html_lower:
                    technologies.append(tech)
                    break

        return list(set(technologies))
