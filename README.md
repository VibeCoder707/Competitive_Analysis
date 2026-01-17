# Competitive Analysis Tool

[![Tests](https://github.com/VibeCoder707/Competitive_Analysis/actions/workflows/tests.yml/badge.svg)](https://github.com/VibeCoder707/Competitive_Analysis/actions/workflows/tests.yml)

CLI tool for comprehensive competitor analysis including web scraping, SEO analysis, news monitoring, and social media tracking.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Add a competitor
compete add stripe --url https://stripe.com --twitter @stripe

# Run analysis
compete analyze stripe --all

# Export results
compete export stripe --format csv
```
