"""Pydantic models for competitors and analysis results."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Competitor(BaseModel):
    """A competitor to track."""

    name: str
    url: HttpUrl | None = None
    twitter: str | None = None
    linkedin: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class WebAnalysisResult(BaseModel):
    """Results from web scraping analysis."""

    title: str | None = None
    description: str | None = None
    headings: list[str] = Field(default_factory=list)
    links_count: int = 0
    images_count: int = 0
    technologies: list[str] = Field(default_factory=list)
    page_size_bytes: int = 0
    load_time_ms: float = 0


class SEOAnalysisResult(BaseModel):
    """Results from SEO analysis."""

    meta_title: str | None = None
    meta_description: str | None = None
    meta_keywords: list[str] = Field(default_factory=list)
    h1_tags: list[str] = Field(default_factory=list)
    h2_tags: list[str] = Field(default_factory=list)
    canonical_url: str | None = None
    robots_meta: str | None = None
    og_tags: dict[str, str] = Field(default_factory=dict)
    structured_data: list[Any] = Field(default_factory=list)


class NewsItem(BaseModel):
    """A single news item about a competitor."""

    title: str
    url: str
    source: str | None = None
    published_at: datetime | None = None
    snippet: str | None = None


class NewsAnalysisResult(BaseModel):
    """Results from news monitoring."""

    items: list[NewsItem] = Field(default_factory=list)
    total_mentions: int = 0


class SocialProfile(BaseModel):
    """Social media profile data."""

    platform: str
    handle: str
    followers: int | None = None
    following: int | None = None
    posts_count: int | None = None
    bio: str | None = None
    verified: bool = False


class SocialAnalysisResult(BaseModel):
    """Results from social media analysis."""

    profiles: list[SocialProfile] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """Combined analysis results for a competitor."""

    competitor_name: str
    analyzed_at: datetime = Field(default_factory=datetime.now)
    web: WebAnalysisResult | None = None
    seo: SEOAnalysisResult | None = None
    news: NewsAnalysisResult | None = None
    social: SocialAnalysisResult | None = None
