diff --git a/README.md b/README.md
index cb5fa57b7f085cedd2c1de7d404170c82dd45b14..92ee2a2a9dca5d30ea1c759042844b53543b3744 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,119 @@
 # Daily Brief Agent
-Bootstrap commit to create default branch.
+
+Daily Brief Agent pulls RSS feeds, stores new items in SQLite with deduplication, generates a
+Markdown daily report, and can optionally send a short Telegram notification. It is designed
+for Python 3.10+ and works smoothly on Windows while remaining cross-platform.
+
+## Features
+
+- Fetch RSS feeds from a YAML configuration file.
+- Store items in SQLite with deterministic IDs to avoid duplicates.
+- Generate a daily Markdown report grouped by category.
+- Optional Telegram notification delivery.
+- CLI with configurable limits and dry-run mode.
+- Logging, tests, and CI configured for Python 3.10–3.12.
+
+## Installation
+
+```bash
+python -m venv .venv
+. .venv/bin/activate  # On Windows: .venv\Scripts\activate
+python -m pip install --upgrade pip
+python -m pip install -e ".[dev]"
+```
+
+## Configuration
+
+Copy `config.yaml` and edit your feeds, storage path, and report directory.
+
+```yaml
+feeds:
+  - name: Example Tech
+    url: https://example.com/rss
+    category: Tech
+
+storage:
+  db_path: agentos.sqlite
+
+reports:
+  output_dir: reports
+
+telegram:
+  enabled: false
+```
+
+To enable Telegram delivery, copy `.env.example` to `.env` and set:
+
+```
+TELEGRAM_BOT_TOKEN=
+TELEGRAM_CHAT_ID=
+```
+
+## CLI Usage
+
+Run the agent:
+
+```bash
+python -m daily_brief_agent --config config.yaml
+```
+
+Common options:
+
+```bash
+python -m daily_brief_agent \
+  --config config.yaml \
+  --max-per-feed 50 \
+  --per-category-limit 30 \
+  --date 2024-01-01
+```
+
+Generate a report without writing to SQLite (preview to stdout):
+
+```bash
+python -m daily_brief_agent --dry-run
+```
+
+Disable Telegram for a single run:
+
+```bash
+python -m daily_brief_agent --no-telegram
+```
+
+Reports are saved to:
+
+```
+reports/YYYY-MM-DD.md
+```
+
+## Windows Task Scheduler
+
+To run daily on Windows:
+
+1. Open **Task Scheduler** → **Create Task...**
+2. **General** tab: set a name like "Daily Brief Agent".
+3. **Triggers** tab: add a new trigger (e.g., daily at 7:00 AM).
+4. **Actions** tab: add a new action.
+   - **Program/script**: `C:\Path\To\Python\python.exe`
+   - **Add arguments**:
+     `-m daily_brief_agent --config C:\Path\To\config.yaml`
+   - **Start in**: `C:\Path\To\Daily-Brief-Agent`
+5. Save the task.
+
+Tip: use absolute paths and ensure your virtual environment is activated by pointing the
+program/script to `.venv\Scripts\python.exe`.
+
+## Troubleshooting
+
+- **Encoding issues on Windows**: use UTF-8 files and avoid non-ASCII paths for config.
+- **Feed errors**: individual feed failures are logged and do not stop the run.
+- **No items**: ensure URLs are reachable and the feeds contain entries.
+- **Telegram not sending**: confirm `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.
+
+## Development
+
+Run linting and tests:
+
+```bash
+ruff check .
+pytest
+```
