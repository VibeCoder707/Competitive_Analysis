"""Export utilities for analysis results."""

import csv
import json
from pathlib import Path

from .models import AnalysisResult


def export_json(result: AnalysisResult, output_path: Path) -> None:
    """Export analysis result to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.model_dump_json(indent=2))


def export_csv(result: AnalysisResult, output_path: Path) -> None:
    """Export analysis result to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    # Flatten the result into rows
    rows.append(["Section", "Field", "Value"])
    rows.append(["Meta", "Competitor", result.competitor_name])
    rows.append(["Meta", "Analyzed At", result.analyzed_at.isoformat()])

    # Web results
    if result.web:
        rows.append(["Web", "Title", result.web.title or ""])
        rows.append(["Web", "Description", result.web.description or ""])
        rows.append(["Web", "Links Count", str(result.web.links_count)])
        rows.append(["Web", "Images Count", str(result.web.images_count)])
        rows.append(["Web", "Page Size (bytes)", str(result.web.page_size_bytes)])
        rows.append(["Web", "Load Time (ms)", f"{result.web.load_time_ms:.2f}"])
        rows.append(["Web", "Technologies", ", ".join(result.web.technologies)])
        for i, heading in enumerate(result.web.headings[:10]):
            rows.append(["Web", f"Heading {i + 1}", heading])

    # SEO results
    if result.seo:
        rows.append(["SEO", "Meta Title", result.seo.meta_title or ""])
        rows.append(["SEO", "Meta Description", result.seo.meta_description or ""])
        rows.append(["SEO", "Meta Keywords", ", ".join(result.seo.meta_keywords)])
        rows.append(["SEO", "Canonical URL", result.seo.canonical_url or ""])
        rows.append(["SEO", "Robots", result.seo.robots_meta or ""])
        for i, h1 in enumerate(result.seo.h1_tags):
            rows.append(["SEO", f"H1 {i + 1}", h1])
        for i, h2 in enumerate(result.seo.h2_tags[:5]):
            rows.append(["SEO", f"H2 {i + 1}", h2])
        for key, value in result.seo.og_tags.items():
            rows.append(["SEO", f"OG: {key}", value])

    # News results
    if result.news:
        rows.append(["News", "Total Mentions", str(result.news.total_mentions)])
        for i, item in enumerate(result.news.items[:10]):
            rows.append(["News", f"Article {i + 1} Title", item.title])
            rows.append(["News", f"Article {i + 1} URL", item.url])
            rows.append(["News", f"Article {i + 1} Source", item.source or ""])

    # Social results
    if result.social:
        for profile in result.social.profiles:
            prefix = f"Social ({profile.platform})"
            rows.append([prefix, "Handle", profile.handle])
            if profile.followers is not None:
                rows.append([prefix, "Followers", str(profile.followers)])
            if profile.bio:
                rows.append([prefix, "Bio", profile.bio])

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
