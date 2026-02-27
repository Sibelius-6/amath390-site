#!/usr/bin/env python3
"""Add xhs_notes frontmatter to each episode file."""
from pathlib import Path

SITE = Path(__file__).parent
EPISODES = SITE / "content" / "episodes"

# Mapping: episode number -> list of (note_id, title)
XHS_NOTES = {
    1: [
        ("698188f0000000000e03ec44", "和弦空间竟然是甜甜圈？音乐里的拓扑学入门"),
        ("6984bb26000000000903b09b", "R L R L R L... 两个字母写完贝多芬第九？"),
    ],
    2: [
        ("69821522000000001a037ea0", "弦振动的秘密（上）｜从物理模型到波动方程"),
        ("6982bd97000000001a024f7b", "弦振动的秘密（下）｜泛音列的数学起源"),
    ],
    3:  [("6985414c000000000b00b3fd", "巴赫的音乐「删不坏」？图连通性给出答案")],
    4:  [("69860e2f000000000a032677", "全音程音列这么罕见？万分之一的数学奇迹")],
    5:  [("69861f8c000000000a03f44e", "从中世纪到文艺复兴｜和声演变的图论优化")],
    6:  [("6987cf26000000000a02aaa2", "15个声部塞进10手指？完美图定理的力量")],
    7:  [("6988f68e000000000a02ddf5", "你觉得混乱？数学说这最均衡")],
    8:  [("6989015d000000000a02ad79", "巴赫骗了你的耳朵270年")],
    9:  [("698d8307000000000a03d479", "你的耳朵会自己造声音")],
    10: [("698e8cf6000000000b010b63", "和声学400年只用了一半对称？")],
    11: [("69965433000000000b012f27", "调好的钢琴为什么还是走音的？")],
    12: [("69974625000000000a02f44c", "超超超超超级Lydian，Jacob的无限音阶")],
    13: [("69975a0c000000000a031b2e", "把节奏越打越快，和弦出来了？")],
}

def add_xhs_notes(path: Path, notes: list):
    text = path.read_text(encoding="utf-8")
    if "xhs_notes:" in text:
        print(f"  {path.name}: already has xhs_notes, skipping")
        return

    # Build the YAML block to insert
    lines = ["xhs_notes:"]
    for note_id, title in notes:
        lines.append(f'  - id: "{note_id}"')
        lines.append(f'    title: "{title}"')
    block = "\n".join(lines) + "\n"

    # Insert before the closing --- of frontmatter
    # Find the second ---
    parts = text.split("---", 2)
    if len(parts) < 3:
        print(f"  {path.name}: could not parse frontmatter")
        return

    new_text = parts[0] + "---" + parts[1] + block + "---" + parts[2]
    path.write_text(new_text, encoding="utf-8")
    print(f"  {path.name}: added {len(notes)} xhs_note(s)")

# Process flat ep files
for ep_num, notes in XHS_NOTES.items():
    flat = EPISODES / f"ep{ep_num:02d}.md"
    bundle = EPISODES / f"ep{ep_num:02d}" / "index.md"
    if flat.exists():
        add_xhs_notes(flat, notes)
    elif bundle.exists():
        add_xhs_notes(bundle, notes)
    else:
        print(f"  ep{ep_num:02d}: file not found")

print("Done.")
