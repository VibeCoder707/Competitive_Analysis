# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
pip install -e .              # Install in development mode
pip install -e ".[dev]"       # Install with dev dependencies
pytest                        # Run all tests
pytest tests/test_file.py     # Run a single test file
```

## CLI Usage

```bash
compete add <name> --url <url> --twitter <handle>   # Add a competitor
compete list                                         # List tracked competitors
compete remove <name>                                # Remove a competitor
compete analyze <name> --all                         # Run all analyses
compete analyze <name> --type web|seo|news|social   # Run specific analysis
compete export <name> --format json|csv             # Export results
```

## Architecture

- `src/competitive_analysis/cli.py` - Click-based CLI entry point
- `src/competitive_analysis/config.py` - Configuration stored in `~/.competitive_analysis/`
- `src/competitive_analysis/models.py` - Pydantic models for competitors and results
- `src/competitive_analysis/exporters.py` - JSON/CSV export utilities
- `src/competitive_analysis/analyzers/` - Pluggable analyzer modules
  - `base.py` - Abstract base with async HTTP and rate limiting
  - `web.py` - Web scraping (httpx + BeautifulSoup)
  - `seo.py` - SEO signals extraction
  - `news.py` - Google News RSS monitoring
  - `social.py` - Social media profile analysis

Key patterns:
- Async-first design using `httpx.AsyncClient`
- All analyzers inherit from `BaseAnalyzer` and implement `analyze()`
- Rate limiting is built into the base class
- Pydantic models for all data structures
