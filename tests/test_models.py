"""Tests for Pydantic models."""

from competitive_analysis.models import (
    AnalysisResult,
    Competitor,
    NewsAnalysisResult,
    NewsItem,
    SEOAnalysisResult,
    SocialAnalysisResult,
    SocialProfile,
    WebAnalysisResult,
)


def test_competitor_creation():
    competitor = Competitor(name="test", url="https://example.com")
    assert competitor.name == "test"
    assert str(competitor.url) == "https://example.com/"


def test_competitor_optional_fields():
    competitor = Competitor(name="test")
    assert competitor.url is None
    assert competitor.twitter is None
    assert competitor.linkedin is None


def test_web_analysis_result_defaults():
    result = WebAnalysisResult()
    assert result.title is None
    assert result.links_count == 0
    assert result.headings == []


def test_seo_analysis_result_defaults():
    result = SEOAnalysisResult()
    assert result.meta_title is None
    assert result.h1_tags == []
    assert result.og_tags == {}


def test_news_item_creation():
    item = NewsItem(title="Test News", url="https://example.com/news")
    assert item.title == "Test News"
    assert item.source is None


def test_news_analysis_result():
    item = NewsItem(title="Test", url="https://example.com")
    result = NewsAnalysisResult(items=[item], total_mentions=1)
    assert len(result.items) == 1
    assert result.total_mentions == 1


def test_social_profile():
    profile = SocialProfile(platform="twitter", handle="@test")
    assert profile.platform == "twitter"
    assert profile.followers is None
    assert profile.verified is False


def test_social_analysis_result():
    profile = SocialProfile(platform="twitter", handle="@test")
    result = SocialAnalysisResult(profiles=[profile])
    assert len(result.profiles) == 1


def test_analysis_result_creation():
    result = AnalysisResult(competitor_name="test")
    assert result.competitor_name == "test"
    assert result.web is None
    assert result.seo is None
    assert result.news is None
    assert result.social is None


def test_analysis_result_with_data():
    result = AnalysisResult(
        competitor_name="test",
        web=WebAnalysisResult(title="Test Site", links_count=10),
        seo=SEOAnalysisResult(meta_title="Test Site"),
    )
    assert result.web.title == "Test Site"
    assert result.seo.meta_title == "Test Site"
