# Daily Brief Agent

A production-ready, cross-platform Python tool that aggregates RSS feeds, deduplicates items in
SQLite, generates a daily Markdown report, and can optionally notify a Telegram chat.

## Features

- Pulls multiple RSS feeds from a YAML config
- Deterministic deduplication using SHA-256 of canonical links
- SQLite storage with indexes for faster reporting
- Daily Markdown report grouped by category and source
- Optional Telegram notification
- Works on Windows, macOS, and Linux

## Quickstart

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

Create a `config.yaml` (example below) and then run:

```bash
daily-brief-agent --config config.yaml
# or
python -m daily_brief_agent --config config.yaml
```

The report will be written to `reports/YYYY-MM-DD.md` by default.

## Configuration

Example `config.yaml`:

```yaml
storage:
  db_path: "daily_brief_agent.sqlite"
  reports_dir: "reports"
feeds:
  - name: "Hacker News"
    url: "https://hnrss.org/frontpage"
    category: "Tech"
delivery:
  telegram:
    enabled: false
timezone: "UTC"
```

Validation is strict. Missing keys, invalid types, or empty feed lists will raise a clear error.
Use `--print-config` to print the loaded config without any secrets.

## CLI Usage

```bash
daily-brief-agent --help
```

Common options:

```bash
# Generate a report for a specific date
daily-brief-agent --date 2024-01-01

# Limit items per feed and per category
daily-brief-agent --max-per-feed 25 --per-category-limit 20

# Include all history, not just items fetched for the target date
daily-brief-agent --include-history

# Disable Telegram even if enabled in config
daily-brief-agent --no-telegram

# Dry run (no DB writes), prints report to stdout
daily-brief-agent --dry-run
```

## Telegram Setup (Optional)

1. Create a bot with [@BotFather](https://t.me/BotFather) and obtain the token.
2. Get the chat ID for your target chat.
3. Create a `.env` file and set:

```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

4. Set `delivery.telegram.enabled: true` in `config.yaml`.

If Telegram is enabled but the environment variables are missing, the app logs a warning and
continues without failing.

## Report Output

Reports are written to `reports/YYYY-MM-DD.md` (relative to the working directory unless an
absolute path is supplied in config). Files are UTF-8 encoded with Unix newlines for
cross-platform compatibility.

## Windows Task Scheduler

To run the agent daily on Windows:

1. Open **Task Scheduler** → **Create Task**.
2. **General** tab:
   - Name: `Daily Brief Agent`
   - Select **Run whether user is logged on or not** (optional)
3. **Triggers** tab:
   - **New...** → Daily → set your preferred time
4. **Actions** tab:
   - **New...** → Action: **Start a program**
   - **Program/script**: `C:\path\to\repo\.venv\Scripts\python.exe`
   - **Add arguments**: `-m daily_brief_agent --config C:\path\to\repo\config.yaml`
   - **Start in**: `C:\path\to\repo`
5. **Conditions** / **Settings** tabs: adjust as needed.

Make sure the virtual environment exists and dependencies are installed.

## Troubleshooting

- **Feed fails to parse**: The log will show `Failed to fetch feed ...`. Verify the URL, or try a
  different RSS source.
- **Invalid config errors**: Check that required keys exist and types are correct.
- **Encoding issues**: Reports are UTF-8. Ensure your editor is using UTF-8 encoding.
- **Telegram not sending**: Confirm `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set and that
  the bot has permission to post to the chat.

## Development

Run formatting and tests locally:

```bash
ruff check .
pytest -q
```
