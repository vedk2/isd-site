"""Download every tab of ISD's Google Sheet and save it into backup/.

Run from the isd-site folder:

    python scripts/refresh_backup.py

Then commit the changed files in backup/. The site uses these copies whenever
the live Sheet can't be reached, so refresh them every few months or after big
edits. A tab is only overwritten if it downloads cleanly and has the right
columns, so a broken Sheet can never wipe out a good backup.
"""

from __future__ import annotations

import logging
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.disable(logging.WARNING)  # hide Streamlit's harmless "No runtime found" message
import config  # noqa: E402
from content import TABS, _fetch_text, _parse_csv  # noqa: E402

logging.disable(logging.NOTSET)


def sheet_urls() -> dict[str, str]:
    urls = dict(config.SHEET_URLS)
    secrets = ROOT / ".streamlit" / "secrets.toml"
    if secrets.exists():
        urls.update({k: v for k, v in tomllib.loads(secrets.read_text()).get("sheets", {}).items() if v})
    return urls


def main() -> int:
    urls = sheet_urls()
    failures = 0
    for key, spec in TABS.items():
        url = urls.get(key, "").strip()
        if not url:
            print(f"SKIP  {spec.sheet_name}: no link set in .streamlit/secrets.toml or config.py")
            failures += 1
            continue
        try:
            text = _fetch_text(url, timeout=20)
            df = _parse_csv(text)
        except Exception as exc:
            print(f"FAIL  {spec.sheet_name}: couldn't download ({exc}). Old backup kept.")
            failures += 1
            continue
        missing = [c for c in spec.required if c not in df.columns]
        if missing:
            print(f"FAIL  {spec.sheet_name}: missing column(s) {', '.join(missing)}. Old backup kept.")
            failures += 1
            continue
        target = config.BACKUP_DIR / spec.backup_file
        text = text.replace("\r\n", "\n")
        target.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        print(f"OK    {spec.sheet_name}: {len(df)} rows -> backup/{spec.backup_file}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
