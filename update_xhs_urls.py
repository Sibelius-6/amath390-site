#!/usr/bin/env python3
"""Parse xhs_urls.txt and update episode frontmatter xhs_notes with correct share URLs."""
import re
from pathlib import Path

SITE = Path(__file__).parent
EPISODES = SITE / "content" / "episodes"
URL_FILE = SITE / "xhs_urls.txt"

# Parse the URL file — extract ep label, title, and URL
entries = {}  # label -> (title, url)
for line in URL_FILE.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    # Extract label (EP01-A, EP02-B, EP03, etc.)
    label_m = re.match(r'^(EP\d+(?:-[AB])?)', line)
    if not label_m:
        continue
    label = label_m.group(1)
    # Extract URL (https://www.xiaohongshu.com/...)
    url_m = re.search(r'(https://www\.xiaohongshu\.com/\S+)', line)
    if not url_m:
        continue
    url = url_m.group(1)
    # Extract title from 【...】
    title_m = re.search(r'【([^】]+) - Sibelius', line)
    title = title_m.group(1) if title_m else label
    entries[label] = (title, url)

print("Parsed entries:")
for k, (t, u) in entries.items():
    print(f"  {k}: {t[:30]}... → {u[:60]}...")

# Group by episode number
ep_notes = {}
for label, (title, url) in entries.items():
    m = re.match(r'EP(\d+)', label)
    if not m:
        continue
    ep = int(m.group(1))
    if ep not in ep_notes:
        ep_notes[ep] = []
    ep_notes[ep].append((title, url))

# Update each episode file's xhs_notes frontmatter
def update_episode(path: Path, notes: list):
    text = path.read_text(encoding="utf-8")

    # Build replacement xhs_notes block
    lines = ["xhs_notes:"]
    for title, url in notes:
        safe_title = title.replace('"', '「').replace('"', '」').replace('"', '\\"')
        lines.append(f'  - title: "{safe_title}"')
        lines.append(f'    url: "{url}"')
    new_block = "\n".join(lines) + "\n"

    # Replace existing xhs_notes block (from "xhs_notes:" to next top-level key or ---)
    # Pattern: xhs_notes: followed by indented lines
    old_block_m = re.search(r'^xhs_notes:(?:\n  [^\n]+)*\n', text, re.MULTILINE)
    if old_block_m:
        text = text[:old_block_m.start()] + new_block + text[old_block_m.end():]
        path.write_text(text, encoding="utf-8")
        print(f"  Updated {path.name}: {len(notes)} note(s)")
    else:
        print(f"  {path.name}: xhs_notes block not found, skipping")

for ep_num, notes in sorted(ep_notes.items()):
    flat = EPISODES / f"ep{ep_num:02d}.md"
    bundle = EPISODES / f"ep{ep_num:02d}" / "index.md"
    if flat.exists():
        update_episode(flat, notes)
    elif bundle.exists():
        update_episode(bundle, notes)
    else:
        print(f"  ep{ep_num:02d}: file not found")

print("\nDone.")
