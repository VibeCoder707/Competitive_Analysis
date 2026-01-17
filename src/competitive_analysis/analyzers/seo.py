"""SEO analyzer for competitor websites."""

import json
import re

from bs4 import BeautifulSoup

from ..models import Competitor, SEOAnalysisResult
from .base import BaseAnalyzer


class SEOAnalyzer(BaseAnalyzer):
    """Analyze competitor websites for SEO signals."""

    @property
    def name(self) -> str:
        return "seo"

    async def analyze(self, competitor: Competitor) -> SEOAnalysisResult | None:
        """Analyze SEO elements of a competitor's website."""
        if not competitor.url:
            return None

        response = await self.fetch_url(str(competitor.url))
        soup = BeautifulSoup(response.text, "lxml")

        # Meta title
        meta_title = None
        if soup.title:
            meta_title = soup.title.string

        # Meta description
        meta_description = None
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        if meta_desc_tag and meta_desc_tag.get("content"):
            meta_description = meta_desc_tag["content"]

        # Meta keywords
        meta_keywords = []
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag and keywords_tag.get("content"):
            meta_keywords = [k.strip() for k in keywords_tag["content"].split(",")]

        # H1 and H2 tags
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]

        # Canonical URL
        canonical_url = None
        canonical_tag = soup.find("link", attrs={"rel": "canonical"})
        if canonical_tag and canonical_tag.get("href"):
            canonical_url = canonical_tag["href"]

        # Robots meta
        robots_meta = None
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        if robots_tag and robots_tag.get("content"):
            robots_meta = robots_tag["content"]

        # Open Graph tags
        og_tags = {}
        for og_tag in soup.find_all("meta", attrs={"property": re.compile(r"^og:")}):
            prop = og_tag.get("property", "")
            content = og_tag.get("content", "")
            if prop and content:
                og_tags[prop] = content

        # Structured data (JSON-LD)
        structured_data = []
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "")
                structured_data.append(data)
            except (json.JSONDecodeError, TypeError):
                pass

        return SEOAnalysisResult(
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            h1_tags=h1_tags,
            h2_tags=h2_tags[:10],  # Limit to first 10
            canonical_url=canonical_url,
            robots_meta=robots_meta,
            og_tags=og_tags,
            structured_data=structured_data[:5],  # Limit to first 5
        )
