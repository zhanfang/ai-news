import sys
import os

# Add src to path to allow imports if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

from src.llm_client import DeepSeekClient
from src.feishu_client import FeishuClient
from src.sources.hacker_news import HackerNewsFetcher
from src.sources.hugging_face import HuggingFaceFetcher
from src.sources.reddit import RedditFetcher
from src.sources.product_hunt import ProductHuntFetcher
from src.sources.github_trending import GitHubTrendingFetcher
from src.sources.techcrunch import TechCrunchFetcher
from src.sources.official_blogs import OfficialBlogsFetcher
from src.database import Database
from src.deduplicator import Deduplicator
from src.content_extractor import ContentExtractor
import concurrent.futures

import argparse

console = Console()

def main():
    parser = argparse.ArgumentParser(description="AI News Aggregator")
    parser.add_argument("--weekly", action="store_true", help="Generate a weekly digest from the database")
    parser.add_argument("--search", type=str, help="Search for news by keyword")
    args = parser.parse_args()

    console.print(Panel.fit("[bold blue]AI News Aggregator[/bold blue]", subtitle="Fetching latest AI updates..."))
    
    # Initialize DB
    # Use absolute path to ensure cron works correctly
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, "news.db")
    db = Database(db_path)
    
    if args.search:
        results = db.search_news(args.search)
        if not results:
            console.print(f"[red]No results found for '{args.search}'[/red]")
        else:
            table = Table(title=f"Search Results: {args.search}", show_header=True)
            table.add_column("Date", style="dim", width=12)
            table.add_column("Source", style="cyan", width=15)
            table.add_column("Title", style="white")
            table.add_column("Link", style="blue")
            
            for item in results:
                # Format date YYYY-MM-DD
                date_str = item.get('sent_at', '')[:10]
                table.add_row(date_str, item.get('source', ''), item.get('title', ''), item.get('url', ''))
            
            console.print(table)
        return

    # Initialize Deduplicator and ContentExtractor
    deduplicator = Deduplicator()
    extractor = ContentExtractor()

    if args.weekly:
        console.print("[bold green]Generating Weekly Digest...[/bold green]")
        all_news = db.get_weekly_news()
        if not all_news:
            console.print("[red]No news found in the last 7 days.[/red]")
            return
        console.print(f"Found {len(all_news)} items from the last 7 days.")
    else:
        # Normal Daily Fetch
        fetchers = [
            ("Official Blogs", OfficialBlogsFetcher()),
            ("Hacker News", HackerNewsFetcher()),
            ("Hugging Face Papers", HuggingFaceFetcher()),
            ("Reddit", RedditFetcher()),
            ("Product Hunt", ProductHuntFetcher()),
            ("GitHub Trending", GitHubTrendingFetcher()),
            ("TechCrunch AI", TechCrunchFetcher())
        ]

        all_news = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            for name, fetcher in fetchers:
                task = progress.add_task(description=f"Fetching from {name}...", total=None)
                try:
                    if hasattr(fetcher, 'fetch'):
                        # Check if fetch accepts arguments (some have defaults)
                        # For simplicity, call without args as defaults are set
                        news = fetcher.fetch()
                        if news:
                            # Filter out already sent news
                            new_items = [item for item in news if db.is_new(item.get('url'))]
                            
                            if new_items:
                                all_items = new_items # Rename for clarity
                                all_news.extend(all_items)
                                console.log(f"[green]✓[/green] Fetched {len(all_items)} new items from {name} (filtered {len(news) - len(all_items)} old)")
                            else:
                                console.log(f"[yellow]![/yellow] No NEW items from {name} (all {len(news)} seen)")
                        else:
                            console.log(f"[yellow]![/yellow] No items found from {name}")
                    else:
                        console.log(f"[red]x[/red] Invalid fetcher: {name}")
                except Exception as e:
                    console.log(f"[red]x[/red] Error fetching {name}: {e}")
                finally:
                    progress.remove_task(task)

        if not all_news:
            console.print("[bold red]No news found![/bold red]")
            return

        # Deduplicate across sources
        console.print(f"[dim]Initial count: {len(all_news)} items[/dim]")
        unique_news = deduplicator.deduplicate(all_news)
        console.print(f"[dim]After deduplication: {len(unique_news)} items (removed {len(all_news) - len(unique_news)} duplicates)[/dim]")
        
        # Use unique news for display and summary
        all_news = unique_news

    # Display results
    table = Table(title="AI News", show_header=True, header_style="bold magenta")
    table.add_column("Source", style="cyan", width=15)
    table.add_column("Title", style="white")
    table.add_column("Link", style="blue")

    # Sort by source for now
    # all_news is already in order of fetchers: HN, HF, Reddit, PH
    # If we take top 30 for summary, and PH is last, it might be cut off if previous sources have many items.
    # Let's shuffle or pick a balanced selection for summary.
    
    # Simple strategy: take top N from each source for summary input
    summary_input = []
    source_counts = {}
    for item in all_news:
        src = item.get('source', 'Unknown')
        # Simplify source name to grouping key
        if "Hacker News" in src: key = "HN"
        elif "Hugging Face" in src: key = "HF"
        elif "Reddit" in src: key = "Reddit"
        elif "Product Hunt" in src: key = "PH"
        elif "GitHub" in src: key = "GH"
        elif "TechCrunch" in src: key = "TC"
        elif "OpenAI" in src or "Anthropic" in src or "DeepMind" in src or "Meta" in src or "Microsoft" in src: key = "Blog"
        else: key = "Other"
        
        if source_counts.get(key, 0) < 50: # Increase per-source limit to 50 to get closer to 150+ total
            summary_input.append(item)
            source_counts[key] = source_counts.get(key, 0) + 1

    # Enhance summary input with full text content (Top 150 items for max coverage)
    # If list is shorter than 150, it takes all.
    top_items = summary_input[:150]
    console.print(f"\n[bold yellow]Extracting content for Top {len(top_items)} items...[/bold yellow]")
    
    def fetch_content(item):
        url = item.get('url')
        if url:
            item['full_content'] = extractor.extract(url)
        return item

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Fetching content...", total=len(top_items))
        # Increase workers to speed up batch extraction
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_item = {executor.submit(fetch_content, item): item for item in top_items}
            for future in concurrent.futures.as_completed(future_to_item):
                progress.advance(task)
    
    for item in all_news:
        # Determine link text
        link = item.get('url', '')
        title = item.get('title', 'No Title')
        source = item.get('source', 'Unknown')
        
        # Truncate title if too long
        if len(title) > 80:
            title = title[:77] + "..."

        table.add_row(source, title, link)

    console.print(table)
    
    # LLM Summary
    console.print("\n[bold yellow]Generating AI Summary...[/bold yellow]")
    
    try:
        llm_client = DeepSeekClient()
        if llm_client.client:
            with console.status("[bold green]Asking DeepSeek to summarize...[/bold green]", spinner="dots"):
                # Pass balanced list to summarizer
                summary = llm_client.summarize(summary_input)
            
            console.print(Panel(Markdown(summary), title="AI Summary (DeepSeek)", border_style="green"))

            # Send to Feishu
            feishu_client = FeishuClient()
            if feishu_client.webhook_url or (feishu_client.app_id and feishu_client.app_secret):
                with console.status("[bold green]Sending to Feishu...[/bold green]", spinner="dots"):
                    # We no longer append the raw list to keep the message focused on high-density summary
                    full_message = summary
                    
                    if args.weekly:
                        title_text = "AI News Weekly Digest"
                    else:
                        title_text = "AI News Daily Digest"

                    result = feishu_client.send_markdown(title_text, full_message)
                    console.log(f"[blue]Feishu Notification:[/blue] {result}")
                    
                    # Mark items as sent in DB only if send successful (or assumed successful)
                    # AND if we are in daily mode (not weekly, as weekly just re-sends old stuff)
                    if result and not args.weekly:
                        for item in summary_input:
                            db.mark_as_sent(item)
                        console.log(f"[green]✓[/green] Marked {len(summary_input)} items as sent in DB")
            else:
                console.print("[yellow]Feishu configuration not found (Webhook or App ID). Skipping notification.[/yellow]")

        else:
            console.print("[yellow]DeepSeek API Key not found. Set DEEPSEEK_API_KEY environment variable to enable AI summaries.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error initializing DeepSeek client: {e}[/bold red]")

if __name__ == "__main__":
    main()
