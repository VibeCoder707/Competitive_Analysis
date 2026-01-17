"""CLI entry point for the competitive analysis tool."""

import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .analyzers import NewsAnalyzer, SEOAnalyzer, SocialAnalyzer, WebAnalyzer
from .config import add_competitor, get_competitor, list_competitors, remove_competitor
from .exporters import export_csv, export_json
from .models import AnalysisResult, Competitor

console = Console()


@click.group()
def main() -> None:
    """Competitive Analysis Tool - Analyze your competitors."""
    pass


@main.command()
@click.argument("name")
@click.option("--url", "-u", help="Competitor website URL")
@click.option("--twitter", "-t", help="Twitter/X handle")
@click.option("--linkedin", "-l", help="LinkedIn profile URL")
def add(name: str, url: str | None, twitter: str | None, linkedin: str | None) -> None:
    """Add a competitor to track."""
    competitor = Competitor(
        name=name,
        url=url,
        twitter=twitter,
        linkedin=linkedin,
    )
    add_competitor(competitor)
    console.print(f"[green]Added competitor:[/green] {name}")

    if url:
        console.print(f"  URL: {url}")
    if twitter:
        console.print(f"  Twitter: {twitter}")
    if linkedin:
        console.print(f"  LinkedIn: {linkedin}")


@main.command("list")
def list_cmd() -> None:
    """List all tracked competitors."""
    competitors = list_competitors()

    if not competitors:
        console.print("[yellow]No competitors tracked yet.[/yellow]")
        console.print("Use 'compete add <name> --url <url>' to add one.")
        return

    table = Table(title="Tracked Competitors")
    table.add_column("Name", style="cyan")
    table.add_column("URL")
    table.add_column("Twitter")
    table.add_column("LinkedIn")

    for c in competitors:
        table.add_row(
            c.name,
            str(c.url) if c.url else "-",
            c.twitter or "-",
            c.linkedin or "-",
        )

    console.print(table)


@main.command()
@click.argument("name")
def remove(name: str) -> None:
    """Remove a competitor from tracking."""
    if remove_competitor(name):
        console.print(f"[green]Removed competitor:[/green] {name}")
    else:
        console.print(f"[red]Competitor not found:[/red] {name}")


@main.command()
@click.argument("name")
@click.option(
    "--type",
    "-t",
    "analysis_type",
    type=click.Choice(["web", "seo", "news", "social"]),
    help="Type of analysis to run",
)
@click.option("--all", "-a", "run_all", is_flag=True, help="Run all analysis types")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv"]),
    default="json",
    help="Output format",
)
def analyze(
    name: str,
    analysis_type: str | None,
    run_all: bool,
    output: str | None,
    output_format: str,
) -> None:
    """Run analysis on a competitor."""
    competitor = get_competitor(name)
    if not competitor:
        console.print(f"[red]Competitor not found:[/red] {name}")
        console.print("Use 'compete list' to see tracked competitors.")
        return

    if not analysis_type and not run_all:
        console.print("[red]Specify --type or --all[/red]")
        return

    result = asyncio.run(_run_analysis(competitor, analysis_type, run_all))

    # Display results
    _display_results(result)

    # Export if output specified
    if output:
        output_path = Path(output)
        if output_format == "json":
            export_json(result, output_path)
        else:
            export_csv(result, output_path)
        console.print(f"\n[green]Results exported to:[/green] {output_path}")


async def _run_analysis(
    competitor: Competitor, analysis_type: str | None, run_all: bool
) -> AnalysisResult:
    """Run the requested analysis types."""
    result = AnalysisResult(competitor_name=competitor.name)

    types_to_run = []
    if run_all:
        types_to_run = ["web", "seo", "news", "social"]
    elif analysis_type:
        types_to_run = [analysis_type]

    analyzers = {
        "web": WebAnalyzer(),
        "seo": SEOAnalyzer(),
        "news": NewsAnalyzer(),
        "social": SocialAnalyzer(),
    }

    for atype in types_to_run:
        analyzer = analyzers[atype]
        console.print(f"[blue]Running {atype} analysis...[/blue]")
        try:
            analysis_result = await analyzer.analyze(competitor)
            setattr(result, atype, analysis_result)
            console.print(f"[green]  {atype} analysis complete[/green]")
        except Exception as e:
            console.print(f"[red]  {atype} analysis failed: {e}[/red]")

    return result


def _display_results(result: AnalysisResult) -> None:
    """Display analysis results in a formatted way."""
    console.print(f"\n[bold]Analysis Results for {result.competitor_name}[/bold]")
    console.print(f"Analyzed at: {result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}\n")

    if result.web:
        console.print("[bold cyan]Web Analysis[/bold cyan]")
        if result.web.title:
            console.print(f"  Title: {result.web.title}")
        if result.web.description:
            console.print(f"  Description: {result.web.description[:100]}...")
        console.print(f"  Links: {result.web.links_count}")
        console.print(f"  Images: {result.web.images_count}")
        console.print(f"  Page size: {result.web.page_size_bytes:,} bytes")
        console.print(f"  Load time: {result.web.load_time_ms:.0f}ms")
        if result.web.technologies:
            console.print(f"  Technologies: {', '.join(result.web.technologies)}")
        console.print()

    if result.seo:
        console.print("[bold cyan]SEO Analysis[/bold cyan]")
        if result.seo.meta_title:
            console.print(f"  Title: {result.seo.meta_title}")
        if result.seo.meta_description:
            console.print(f"  Description: {result.seo.meta_description[:100]}...")
        if result.seo.h1_tags:
            console.print(f"  H1 tags: {len(result.seo.h1_tags)}")
        if result.seo.canonical_url:
            console.print(f"  Canonical: {result.seo.canonical_url}")
        if result.seo.og_tags:
            console.print(f"  OG tags: {len(result.seo.og_tags)} found")
        console.print()

    if result.news:
        console.print("[bold cyan]News Mentions[/bold cyan]")
        console.print(f"  Total mentions found: {result.news.total_mentions}")
        for item in result.news.items[:5]:
            console.print(f"  - {item.title[:60]}...")
            if item.source:
                console.print(f"    Source: {item.source}")
        console.print()

    if result.social:
        console.print("[bold cyan]Social Media[/bold cyan]")
        for profile in result.social.profiles:
            console.print(f"  {profile.platform}: {profile.handle}")
            if profile.followers:
                console.print(f"    Followers: {profile.followers:,}")
            if profile.bio:
                console.print(f"    Bio: {profile.bio[:80]}...")
        console.print()


@main.command()
@click.argument("name")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "csv"]),
    default="json",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def export(name: str, output_format: str, output: str | None) -> None:
    """Export stored analysis results."""
    competitor = get_competitor(name)
    if not competitor:
        console.print(f"[red]Competitor not found:[/red] {name}")
        return

    # For now, run a fresh analysis and export
    # In a full implementation, you'd store and retrieve past results
    console.print("[yellow]Running fresh analysis for export...[/yellow]")
    result = asyncio.run(_run_analysis(competitor, None, True))

    if output:
        output_path = Path(output)
    else:
        output_path = Path(f"output/{name}_analysis.{output_format}")

    if output_format == "json":
        export_json(result, output_path)
    else:
        export_csv(result, output_path)

    console.print(f"[green]Exported to:[/green] {output_path}")


if __name__ == "__main__":
    main()
