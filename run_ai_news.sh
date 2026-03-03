#!/bin/bash

# Project directory
PROJECT_DIR="/Users/bytedance/Documents/code/github/ai-news-aggregator"
LOG_FILE="$PROJECT_DIR/cron.log"

# Change to project directory to ensure relative paths work
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source "$PROJECT_DIR/.venv/bin/activate"

# Log start time
echo "Starting AI News Aggregator at $(date)" >> "$LOG_FILE"

# Run the script and append output to log
# Using unbuffered output (-u) to see logs immediately
python3 -u "$PROJECT_DIR/src/main.py" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Finished successfully at $(date)" >> "$LOG_FILE"
else
    echo "Failed with exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

echo "----------------------------------------" >> "$LOG_FILE"

# Deactivate
deactivate
