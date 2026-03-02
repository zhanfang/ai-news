#!/bin/bash

# Project directory
PROJECT_DIR="/Users/bytedance/Documents/code/github/ai-news-aggregator"

# Activate virtual environment
source "$PROJECT_DIR/.venv/bin/activate"

# Source global profile to load environment variables (cron doesn't load .zshrc by default)
if [ -f "$HOME/.zshrc" ]; then
    # We only want the exports, but sourcing full zshrc might be noisy or interactive.
    # A safer way for cron is to manually export the known vars if sourcing fails or is too heavy.
    # However, let's try to source it. If it fails, we rely on the user having set them in crontab or elsewhere.
    # A better approach for cron is to explicitly source the file containing the vars.
    source "$HOME/.zshrc" > /dev/null 2>&1
fi

# Load local .env as fallback/override if it exists
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(cat "$PROJECT_DIR/.env" | grep -v '^#' | xargs)
fi

# Run the script
# Use --headless or similar if you add arguments later
python3 "$PROJECT_DIR/src/main.py"

# Deactivate (optional in script, but good practice)
deactivate
