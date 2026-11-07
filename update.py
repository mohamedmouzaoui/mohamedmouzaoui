#! /usr/bin/env python3 
"""Generates dark_mode.svg and light_mode.svg (neofetch-style profile card).

Edit the CARD section below to change the text. Run `python update.py`
locally, or let the GitHub Action run it every day to refresh the stats.
Only the Python standard library is used.
"""
import json
import math
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

USERNAME = "mohamedmouzaoui"

# ----------------------------------------------------------------- CARD ---
# ("Key", "Value")  ·  None = blank line  ·  "# Title" = section header
CARD = [
    ("Role", "Cybersecurity Analyst"),
    ("Focus", "Detection & Security Automation"),
    ("Award", "Best Startup Work (Sentinel XDR Pro)"),
    None,
    ("Languages.Programming", "Python, JavaScript"),
    ("Stack.Dev", "FastAPI, React, Docker"),
    ("Stack.Data", "Elasticsearch, PostgreSQL, Redis, Grafana"),
    ("Detection", "MITRE ATT&CK, Sigma, SOAR, ML"),
    ("Languages.Real", "Arabic, English, French, Spanish, Italian"),
    None,
    ("Hobbies.Software", "CTFs, Game Dev (Godot, UE4)"),
    ("Hobbies.Other", "Cybersecurity content creation"),
    None,
    "# Contact",
    ("Email.Personal", "mehamedm.hz11222@gmail.com"),
    ("LinkedIn", "mohamed-mouzaoui-19ab8740a"),
    ("GitHub", USERNAME),
    None,
    "# GitHub Stats",
    ("Repos", "{repos}"),
    ("Stars", "{stars}"),
    ("Commits", "{commits}"),
    ("Followers", "{followers}"),
]
HEADER = "mohamed@mouzaoui"
ART_TAGLINE = ["mo.life", "detect · automate · respond"]

THEMES = {
    "dark_mode.svg": dict(bg="#0d1117", text="#c9d1d9", key="#e8832a",
                          dots="#484f58", art="#8b949e", accent="#e8832a"),
    "light_mode.svg": dict(bg="#f6f8fa", text="#24292f", key="#c2410c",
                           dots="#8c959f", art="#57606a", accent="#c2410c"),
}

# --------------------------------------------------------------- LAYOUT ---
FONT = 14
CW = 8.4          # approx. width of one monospace character (px)
LH = 20           # line height (px)
KEY_COL = 26      # key + dots take this many characters
LINE_COLS = 72    # width of header / section rules
ART_COLS = 40
PAD = 24

# ---------------------------------------------------------------- STATS ---
def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "profile-card"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_stats():
    stats = {"repos": "—", "stars": "—", "commits": "—", "followers": "—"}
    try:
        user = api(f"/users/{USERNAME}")
        stats["repos"] = user["public_repos"]
        stats["followers"] = user["followers"]
        stars, page = 0, 1
        while True:
            repos = api(f"/users/{USERNAME}/repos?per_page=100&page={page}")
            stars += sum(r["stargazers_count"] for r in repos)
            if len(repos) < 100:
                break
            page += 1
        stats["stars"] = stars
    except Exception as e:  # keep going with whatever we have
        print("stats (profile) failed:", e, file=sys.stderr)
    try:
        stats["commits"] = api(f"/search/commits?q=author:{USERNAME}")["total_count"]
    except Exception as e:
        print("stats (commits) failed:", e, file=sys.stderr)
    return {k: f"{v:,}" if isinstance(v, int) else v for k, v in stats.items()}


# ------------------------------------------------------------------ ART ---
def make_art(cols, rows):
    """ASCII ring with an 'M' inside, like the mo.life logo."""
    cx, cy = cols * CW / 2, rows * LH / 2
    R = min(cx, cy) - 4
    ring_w = 26
    seg = []
    mw, mh = R * 0.52, R * 0.50           # half width / half height of the M
    top, bot = cy - mh, cy + mh
    seg += [((cx - mw, bot), (cx - mw, top)), ((cx + mw, bot), (cx + mw, top)),
            ((cx - mw, top), (cx, cy + mh * 0.15)), ((cx, cy + mh * 0.15), (cx + mw, top))]

    def dist(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

    out = []
    for r in range(rows):
        row = ""
        for c in range(cols):
            p = (c * CW + CW / 2, r * LH + LH / 2)
            d = math.hypot(p[0] - cx, p[1] - cy)
            if abs(d - R) < ring_w / 2:
                row += "@" if abs(d - R) < ring_w / 4 else "%"
            elif d < R - ring_w and min(dist(p, a, b) for a, b in seg) < 17:
                row += "#"
            elif d < R - ring_w and (c + r) % 3 == 0 and d > R * 0.78:
                row += "."
            else:
                row += " "
        out.append(row.rstrip())
    return out


# ------------------------------------------------------------------ SVG ---
def build(theme, stats):
    right = []  # list of (kind, payload)
    right.append(("rule", HEADER))
    for item in CARD:
        if item is None:
            right.append(("blank", None))
        elif isinstance(item, str):
            right.append(("rule", item.lstrip("# ")))
        else:
            k, v = item
            right.append(("kv", (k, v.format(**stats))))

    n = len(right)
    art_rows = min(n - 4, 20)
    art = make_art(ART_COLS, art_rows)
    art_top = max(0, (n - art_rows - 3) // 2)
    x_art = PAD
    x_txt = PAD + ART_COLS * CW + 24
    width = round(x_txt + LINE_COLS * CW + PAD)
    height = n * LH + PAD * 2 - 4

    t = []
    t.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" font-family="Consolas, \'DejaVu Sans Mono\', '
             f'\'Courier New\', monospace" font-size="{FONT}">')
    t.append(f'<rect width="100%" height="100%" rx="10" fill="{theme["bg"]}"/>')
    t.append('<style>text{white-space:pre}</style>')

    # left: ASCII art + tagline
    for i, line in enumerate(art):
        y = PAD + (art_top + i) * LH + FONT
        t.append(f'<text x="{x_art}" y="{y}" fill="{theme["art"]}" xml:space="preserve">{escape(line)}</text>')
    yb = PAD + (art_top + art_rows + 1) * LH + FONT
    for j, line in enumerate(ART_TAGLINE):
        x = x_art + (ART_COLS - len(line)) * CW / 2
        fill = theme["accent"] if j == 0 else theme["art"]
        weight = "bold" if j == 0 else "normal"
        t.append(f'<text x="{x:.1f}" y="{yb + j * LH}" fill="{fill}" font-weight="{weight}">{escape(line)}</text>')

    # right: info
    for i, (kind, payload) in enumerate(right):
        y = PAD + i * LH + FONT
        if kind == "blank":
            t.append(f'<text x="{x_txt:.1f}" y="{y}" fill="{theme["dots"]}">.</text>')
        elif kind == "rule":
            title = f" {payload} " if i else f"{payload} "
            head = f"{title}" if i else title
            if i == 0:
                line = escape(head)
                t.append(f'<text x="{x_txt:.1f}" y="{y}" fill="{theme["accent"]}" font-weight="bold" xml:space="preserve">'
                         f'{line}<tspan fill="{theme["dots"]}" font-weight="normal">{"─" * (LINE_COLS - len(head))}</tspan></text>')
            else:
                lead = "─ "
                rest = LINE_COLS - len(lead) - len(payload) - 1
                t.append(f'<text x="{x_txt:.1f}" y="{y}" fill="{theme["dots"]}" xml:space="preserve">{lead}'
                         f'<tspan fill="{theme["accent"]}" font-weight="bold">{escape(payload)}</tspan> {"─" * rest}</text>')
        else:
            k, v = payload
            dots = "." * max(2, KEY_COL - len(k) - 2)
            t.append(f'<text x="{x_txt:.1f}" y="{y}" fill="{theme["text"]}" xml:space="preserve">'
                     f'<tspan fill="{theme["dots"]}">. </tspan>'
                     f'<tspan fill="{theme["key"]}">{escape(k)}:</tspan>'
                     f'<tspan fill="{theme["dots"]}"> {dots} </tspan>{escape(v)}</text>')
    t.append("</svg>")
    return "\n".join(t)


def main():
    stats = fetch_stats()
    here = os.path.dirname(os.path.abspath(__file__))
    for name, theme in THEMES.items():
        with open(os.path.join(here, name), "w", encoding="utf-8") as f:
            f.write(build(theme, stats))
    print("done:", stats)


if __name__ == "__main__":
    main()
