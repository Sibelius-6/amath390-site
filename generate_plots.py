#!/usr/bin/env python3
"""
Extracts matplotlib code blocks from episode markdown files,
renders them to PNG, and replaces the code blocks with <img> tags.

Usage:
    python generate_plots.py ep24 ep25 ep27 ep28 ep29
    python generate_plots.py ep26 ep30 ep31   # after translation agents finish
    python generate_plots.py all              # process all episodes
"""
import re
import sys
import os
import subprocess
import textwrap
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONTENT_DIR = SCRIPT_DIR / "content" / "episodes"
STATIC_DIR = SCRIPT_DIR / "static" / "images"

# Prefix comment patterns that label a figure (used for naming PNG files)
FIGURE_LABEL_RE = re.compile(r"#\s*Figure:\s*(.+)", re.IGNORECASE)

# Match a fenced python code block
CODE_BLOCK_RE = re.compile(
    r"```python\n(.*?)\n```",
    re.DOTALL,
)

def slugify(text: str) -> str:
    """Convert figure label to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text[:60]


def extract_figure_label(code: str) -> str | None:
    """Return the figure label comment from the first few lines."""
    for line in code.splitlines()[:5]:
        m = FIGURE_LABEL_RE.search(line)
        if m:
            return m.group(1).strip()
    return None


def make_output_code(code: str, output_path: Path) -> str:
    """Patch the code block: replace plt.show() with plt.savefig()."""
    # Remove any existing plt.show() and plt.close() calls
    code = re.sub(r"\bplt\.show\(\)", "", code)
    code = re.sub(r"\bplt\.close\(\)", "", code)
    # Add non-interactive backend at top (before any import)
    header = "import matplotlib\nmatplotlib.use('Agg')\n"
    # Replace inline savefig calls if the code already has one
    if "plt.savefig" not in code:
        # Append save + close at the end
        code = code.rstrip() + f"\nplt.savefig({str(output_path)!r}, dpi=150, bbox_inches='tight')\nplt.close('all')\n"
    else:
        # Patch existing savefig to our path
        code = re.sub(
            r"plt\.savefig\([^)]+\)",
            f"plt.savefig({str(output_path)!r}, dpi=150, bbox_inches='tight')",
            code,
        )
        code = code.rstrip() + "\nplt.close('all')\n"
    return header + code


def process_episode(ep: str) -> None:
    ep = ep.lower().strip()
    if not ep.startswith("ep"):
        ep = "ep" + ep
    md_path = CONTENT_DIR / f"{ep}.md"
    if not md_path.exists():
        print(f"  [skip] {md_path} not found")
        return

    out_dir = STATIC_DIR / ep
    out_dir.mkdir(parents=True, exist_ok=True)

    content = md_path.read_text(encoding="utf-8")
    counter = [0]
    errors = []

    def replace_block(m: re.Match) -> str:
        code = m.group(1)

        # Only process blocks that contain matplotlib
        if "import matplotlib" not in code and "import pyplot" not in code:
            return m.group(0)

        counter[0] += 1
        label = extract_figure_label(code)
        if label:
            filename = f"fig{counter[0]:02d}_{slugify(label)}.png"
            alt_text = label
        else:
            filename = f"fig{counter[0]:02d}.png"
            alt_text = f"{ep.upper()} figure {counter[0]}"

        output_path = out_dir / filename
        web_path = f"/images/{ep}/{filename}"

        # Don't re-render if the PNG already exists
        if output_path.exists():
            print(f"  [exists] {filename}")
        else:
            patched = make_output_code(code, output_path)
            result = subprocess.run(
                ["python3", "-c", patched],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(SCRIPT_DIR),
            )
            if result.returncode != 0:
                print(f"  [ERROR] {filename}:\n{result.stderr[-800:]}")
                errors.append(filename)
                return m.group(0)  # leave original code block on error
            print(f"  [ok] {filename}")

        # Build the replacement HTML
        img_tag = (
            f'<figure>\n'
            f'<img src="{web_path}" alt="{alt_text}" style="max-width:100%;border-radius:4px">\n'
            f'<figcaption>{alt_text}</figcaption>\n'
            f'</figure>'
        )
        return img_tag

    new_content = CODE_BLOCK_RE.sub(replace_block, content)

    if new_content != content:
        md_path.write_text(new_content, encoding="utf-8")
        print(f"  Updated {md_path.name}")
    else:
        print(f"  No changes to {md_path.name}")

    if errors:
        print(f"  WARNING: {len(errors)} figure(s) failed to render: {errors}")


def main():
    args = sys.argv[1:]
    if not args or args == ["all"]:
        episodes = [f"ep{n}" for n in range(24, 32)]
    else:
        episodes = args

    for ep in episodes:
        print(f"\nProcessing {ep}...")
        process_episode(ep)

    print("\nDone.")


if __name__ == "__main__":
    main()
