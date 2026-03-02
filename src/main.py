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

console = Console()

def main():
    console.print(Panel.fit("[bold blue]AI News Aggregator[/bold blue]", subtitle="Fetching latest AI updates..."))

    fetchers = [
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
                        all_news.extend(news)
                        console.log(f"[green]✓[/green] Fetched {len(news)} items from {name}")
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

    # Display results
    table = Table(title="Latest AI News", show_header=True, header_style="bold magenta")
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
        else: key = "Other"
        
        if source_counts.get(key, 0) < 10: # Take up to 10 from each source (adjusted to accommodate more sources)
            summary_input.append(item)
            source_counts[key] = source_counts.get(key, 0) + 1

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
                    # Append original news list to the message
                    news_list_md = "\n\n---\n**Original News List:**\n"
                    for item in all_news[:30]: # Limit to top 30 to avoid message size limits
                        title = item.get('title', 'No Title')
                        url = item.get('url', '#')
                        source = item.get('source', 'Unknown')
                        news_list_md += f"- [{title}]({url}) ({source})\n"
                    
                    full_message = summary + news_list_md
                    
                    result = feishu_client.send_markdown("AI News Daily Digest", full_message)
                    console.log(f"[blue]Feishu Notification:[/blue] {result}")
            else:
                console.print("[yellow]Feishu configuration not found (Webhook or App ID). Skipping notification.[/yellow]")

        else:
            console.print("[yellow]DeepSeek API Key not found. Set DEEPSEEK_API_KEY environment variable to enable AI summaries.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error initializing DeepSeek client: {e}[/bold red]")

if __name__ == "__main__":
    main()
