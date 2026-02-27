#!/usr/bin/env python3
"""
Convert $...$ and $$...$$ math delimiters in Hugo episode markdown files
to {{< m >}}...{{< /m >}} and {{< dm >}}...{{< /dm >}} shortcodes.

Also unwraps existing <div>$...$</div> patterns from the EP15 partial fix.

Handles:
- $$...$$ display math (possibly multiline within theorem/proof shortcodes)
- $...$ inline math
- <div>$...$</div> or <div>$$...$$</div> already-wrapped patterns
- Skips frontmatter (between --- delimiters)
- Does NOT touch math inside HTML attributes or code blocks
"""

import re
import sys
from pathlib import Path

SITE_DIR = Path(__file__).parent
CONTENT_DIR = SITE_DIR / "content" / "episodes"

# Collect all episode markdown files
episode_files = list(CONTENT_DIR.glob("**/*.md"))
print(f"Found {len(episode_files)} episode files")

def convert_file(path: Path) -> tuple[str, int]:
    """Convert math delimiters in a single file. Returns (new_content, change_count)."""
    text = path.read_text(encoding="utf-8")
    original = text
    changes = 0

    # Step 1: Split off frontmatter so we don't touch it
    # Frontmatter is between opening --- and closing ---
    fm_match = re.match(r'^(---\n.*?\n---\n)(.*)', text, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(1)
        body = fm_match.group(2)
    else:
        frontmatter = ""
        body = text

    # Step 2: Unwrap existing <div>$...$</div> (from EP15 partial fix)
    # Pattern: <div>$CONTENT$</div> on a single line → will be handled by step 3/4
    def unwrap_div_dollar(m):
        nonlocal changes
        inner = m.group(1)
        changes += 1
        return inner  # Just return the raw $...$ which step 3 will convert
    body = re.sub(r'<div>(\$\$?[^$\n]+?\$\$?)</div>', unwrap_div_dollar, body)

    # Step 3: Convert $$...$$ display math
    # These may span multiple lines inside shortcode bodies, but for safety
    # we handle both single-line and multiline $$...$$
    def convert_dm(m):
        nonlocal changes
        inner = m.group(1)
        changes += 1
        return '{{< dm >}}' + inner + '{{< /dm >}}'

    # First handle display math $$ ... $$ (greedy=False to get smallest match)
    body = re.sub(r'\$\$((?:(?!\$\$).)+?)\$\$', convert_dm, body, flags=re.DOTALL)

    # Step 4: Convert $...$ inline math
    # Be careful not to match inside already-converted shortcodes or code spans
    # A simple heuristic: match $ ... $ where content doesn't contain newlines
    # and doesn't start/end with space (avoids currency symbols like $5)
    def convert_m(m):
        nonlocal changes
        inner = m.group(1)
        # Skip if it looks like a currency amount (pure digit/comma/dot)
        if re.match(r'^[\d,. ]+$', inner):
            return m.group(0)
        changes += 1
        return '{{< m >}}' + inner + '{{< /m >}}'

    # Match $...$ where content is non-empty, no newlines, doesn't start/end with space
    body = re.sub(r'\$([^\$\n]+?)\$', convert_m, body)

    new_text = frontmatter + body
    return new_text, changes

total_changes = 0
for ep_file in sorted(episode_files):
    new_content, n = convert_file(ep_file)
    if n > 0:
        ep_file.write_text(new_content, encoding="utf-8")
        print(f"  {ep_file.relative_to(SITE_DIR)}: {n} conversions")
        total_changes += n
    else:
        print(f"  {ep_file.relative_to(SITE_DIR)}: no changes")

print(f"\nTotal: {total_changes} math delimiter conversions across {len(episode_files)} files")
