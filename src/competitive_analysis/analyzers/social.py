"""Social media analyzer for competitor profiles."""

import re

from bs4 import BeautifulSoup

from ..models import Competitor, SocialAnalysisResult, SocialProfile
from .base import BaseAnalyzer


class SocialAnalyzer(BaseAnalyzer):
    """Analyze competitor social media presence."""

    @property
    def name(self) -> str:
        return "social"

    async def analyze(self, competitor: Competitor) -> SocialAnalysisResult:
        """Analyze social media profiles of a competitor."""
        profiles = []

        # Analyze Twitter/X profile if handle provided
        if competitor.twitter:
            twitter_profile = await self._analyze_twitter(competitor.twitter)
            if twitter_profile:
                profiles.append(twitter_profile)

        # Analyze LinkedIn if provided
        if competitor.linkedin:
            linkedin_profile = await self._analyze_linkedin(competitor.linkedin)
            if linkedin_profile:
                profiles.append(linkedin_profile)

        return SocialAnalysisResult(profiles=profiles)

    async def _analyze_twitter(self, handle: str) -> SocialProfile | None:
        """Analyze a Twitter/X profile (public data only)."""
        # Clean handle
        handle = handle.lstrip("@")

        # Note: Twitter/X now requires authentication for most API access
        # This returns a basic profile structure
        # For production use, you'd integrate with Twitter API v2
        return SocialProfile(
            platform="twitter",
            handle=f"@{handle}",
            followers=None,
            following=None,
            posts_count=None,
            bio=None,
            verified=False,
        )

    async def _analyze_linkedin(self, profile_url: str) -> SocialProfile | None:
        """Analyze a LinkedIn profile (limited public data)."""
        # Note: LinkedIn heavily restricts scraping
        # For production use, you'd need LinkedIn API access
        try:
            response = await self.fetch_url(profile_url)
            soup = BeautifulSoup(response.text, "lxml")

            # Try to extract basic info from public profile
            name = None
            title_tag = soup.find("title")
            if title_tag and title_tag.string:
                # LinkedIn titles are usually "Name | LinkedIn"
                name = title_tag.string.split("|")[0].strip()

            bio = None
            about_section = soup.find("section", class_=re.compile(r"about"))
            if about_section:
                bio = about_section.get_text(strip=True)[:200]

            return SocialProfile(
                platform="linkedin",
                handle=profile_url,
                bio=bio,
            )
        except Exception:
            return SocialProfile(
                platform="linkedin",
                handle=profile_url,
            )
