"""
Mass UI Component Scraper - Extended version
Scrapes 25+ repos to collect 500+ production-quality components
"""
import asyncio
import json
from pathlib import Path
from ui_pattern_scraper import UIPatternScraper

async def main():
    """Run massive scraping job across 25+ repos."""

    # Load scraping sources
    sources_path = Path("backend/scrapers/scraping_sources.json")
    with open(sources_path) as f:
        config = json.load(f)

    # Filter by priority
    critical = [s["repo"] for s in config["sources"] if s["priority"] == "critical"]
    high = [s["repo"] for s in config["sources"] if s["priority"] == "high"]
    medium = [s["repo"] for s in config["sources"] if s["priority"] == "medium"]

    all_repos = critical + high + medium

    print("🚀 MASS UI COMPONENT SCRAPING JOB")
    print("=" * 80)
    print(f"📊 Target Repos: {len(all_repos)}")
    print(f"   Critical: {len(critical)}")
    print(f"   High: {len(high)}")
    print(f"   Medium: {len(medium)}")
    print()
    print("📋 Repos to scrape:")
    for repo in all_repos[:15]:  # Show first 15
        print(f"   - {repo}")
    if len(all_repos) > 15:
        print(f"   ... and {len(all_repos) - 15} more")
    print()

    # Create scraper
    scraper = UIPatternScraper()

    # Run scraping
    patterns = await scraper.run_scraping_job(sources=all_repos)

    # Summary
    print("\n" + "=" * 80)
    print("✅ SCRAPING COMPLETE!")
    print("=" * 80)
    print(f"📦 Total Components Extracted: {len(patterns)}")
    print()

    # Breakdown by framework
    frameworks = {}
    for p in patterns:
        fw = p.get("framework", "unknown")
        frameworks[fw] = frameworks.get(fw, 0) + 1

    print("🎯 By Framework:")
    for fw, count in sorted(frameworks.items(), key=lambda x: x[1], reverse=True):
        print(f"   {fw}: {count}")
    print()

    # Breakdown by category
    categories = {}
    for p in patterns:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print("📁 By Category (Top 10):")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {cat}: {count}")
    print()

    # Breakdown by styling
    styling = {}
    for p in patterns:
        st = p.get("styling", "unknown")
        styling[st] = styling.get(st, 0) + 1

    print("🎨 By Styling:")
    for st, count in sorted(styling.items(), key=lambda x: x[1], reverse=True):
        print(f"   {st}: {count}")
    print()

    print(f"💾 All patterns saved to: backend/data/ui_patterns.db")
    print()
    print("🎉 Ready for:")
    print("   ✅ Quality scoring")
    print("   ✅ Screenshot generation")
    print("   ✅ Semantic search")
    print("   ✅ Agent integration")

if __name__ == "__main__":
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")
    asyncio.run(main())
