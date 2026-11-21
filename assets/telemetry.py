"""Genera las animaciones del perfil con datos reales de GitHub.

Uso: GH_TOKEN=... python assets/telemetry.py [carpeta_salida]
Crea engine-room.svg, telemetry.svg y starfield.svg. La GitHub Action lo corre cada día
y publica los archivos en la rama `output`.
"""

import json
import math
import os
import random
import sys
import urllib.request
from pathlib import Path

USER = "C0z1"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
OUT.mkdir(parents=True, exist_ok=True)

BG = "#0b0a1f"
VIOLET = "#a78bfa"
CYAN = "#7dd3fc"
PINK = "#f0abfc"
TEXT = "#e8e6ff"
MUTED = "#8b87b5"
FONT = "Fira Code, JetBrains Mono, Consolas, monospace"

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes { stargazerCount languages(first: 10) { edges { size node { name color } } } }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""


def github():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def defs():
    return f"""<defs>
<linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0a1f"/><stop offset="1" stop-color="#140a33"/></linearGradient>
<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset="0.85" stop-color="{VIOLET}" stop-opacity="0.18"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0.55"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>"""


def frame(w, h, title):
    return (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="url(#panel)" stroke="{VIOLET}" stroke-opacity="0.35"/>'
        f'<circle cx="22" cy="22" r="4" fill="#f87171"/><circle cx="36" cy="22" r="4" fill="#fbbf24"/><circle cx="50" cy="22" r="4" fill="#4ade80"/>'
        f'<text x="{w / 2}" y="26" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}" letter-spacing="3">{title}</text>'
        f'<line x1="14" y1="40" x2="{w - 14}" y2="40" stroke="{VIOLET}" stroke-opacity="0.18"/>'
    )


def scanner(w, h, dur=5):
    return (
        f'<rect x="-120" y="41" width="120" height="{h - 42}" fill="url(#beam)">'
        f'<animate attributeName="x" values="-120;{w}" dur="{dur}s" repeatCount="indefinite"/></rect>'
    )


# ---------------------------------------------------------------- Engine room

STACK = [
    ("LANGUAGES", ["Python", "TypeScript", "JavaScript", "C++", "SQL", "Bash"], VIOLET),
    ("BACKEND", ["Django", "FastAPI", "PostgreSQL", "SQL Server", "DuckDB", "ZeroMQ"], CYAN),
    ("FRONTEND", ["React", "Next.js", "Tailwind", "Three.js", "Electron", "Tauri"], PINK),
    ("AI", ["Claude", "DeepSeek", "LLaMA", "Multi-agent", "Whisper", "scikit-learn"], "#c4b5fd"),
    ("INFRA", ["Docker", "GitHub Actions", "Cloudflare", "AWS", "Arch Linux", "Ubuntu"], "#93c5fd"),
]


def engine_room():
    w, h = 900, 300
    rows = []
    y0 = 78
    for i, (cat, items, color) in enumerate(STACK):
        y = y0 + i * 44
        rows.append(
            f'<text x="34" y="{y + 5}" font-family="{FONT}" font-size="12" fill="{color}" letter-spacing="2" opacity="0">'
            f'{cat}<animate attributeName="opacity" values="0;1" begin="{0.2 + i * 0.35}s" dur="0.4s" fill="freeze"/></text>'
        )
        x = 160
        for j, item in enumerate(items):
            tw = 14 + len(item) * 8
            begin = 0.35 + i * 0.35 + j * 0.12
            rows.append(
                f'<g opacity="0"><animate attributeName="opacity" values="0;1" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 6;0 0" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
                f'<rect x="{x}" y="{y - 12}" width="{tw}" height="24" rx="6" fill="{color}" fill-opacity="0.08" stroke="{color}" stroke-opacity="0.45">'
                f'<animate attributeName="stroke-opacity" values="0.45;0.9;0.45" dur="{3 + (i + j) % 4}s" begin="{begin + 1:.2f}s" repeatCount="indefinite"/></rect>'
                f'<text x="{x + tw / 2}" y="{y + 4.5}" text-anchor="middle" font-family="{FONT}" font-size="12.5" fill="{TEXT}">{item}</text></g>'
            )
            x += tw + 10
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Tech stack">'
        f"{defs()}{frame(w, h, 'ENGINE ROOM')}{''.join(rows)}{scanner(w, h, 6)}</svg>"
    )


# ---------------------------------------------------------------- Telemetry

# Lenguajes de maquetado que inflan el conteo sin decir nada del trabajo
SKIP_LANGS = {"HTML", "CSS", "SCSS", "Jupyter Notebook"}


def telemetry(u):
    w, h = 900, 300
    repos = u["repositories"]["totalCount"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    cc = u["contributionsCollection"]
    commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    contrib = cc["contributionCalendar"]["totalContributions"]
    days = cc["contributionCalendar"]["weeks"]
    active = sum(1 for wk in days for d in wk["contributionDays"] if d["contributionCount"] > 0)

    langs = {}
    for n in u["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            name = e["node"]["name"]
            if name in SKIP_LANGS:
                continue
            langs.setdefault(name, [0, e["node"]["color"] or VIOLET])
            langs[name][0] += e["size"]
    total = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]

    del stars  # con pocas estrellas no suma; se muestran días activos
    metrics = [("COMMITS / YEAR", commits), ("CONTRIBUTIONS", contrib), ("PUBLIC REPOS", repos), ("ACTIVE DAYS", active)]
    parts = []
    for i, (label, value) in enumerate(metrics):
        x, y = 40 + (i % 2) * 190, 92 + (i // 2) * 96
        parts.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1" begin="{0.2 + i * 0.25}s" dur="0.5s" fill="freeze"/>'
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="2">{label}</text>'
            f'<text x="{x}" y="{y + 42}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="38" font-weight="700" fill="{TEXT}" filter="url(#glow)">{value:,}</text></g>'
        )
    # anillo de "señal" que gira
    parts.append(
        f'<g transform="translate(440 160)"><circle r="46" fill="none" stroke="{VIOLET}" stroke-opacity="0.15"/>'
        f'<circle r="46" fill="none" stroke="{CYAN}" stroke-width="2" stroke-dasharray="40 250" stroke-linecap="round">'
        f'<animateTransform attributeName="transform" type="rotate" values="0;360" dur="4s" repeatCount="indefinite"/></circle>'
        f'<circle r="30" fill="none" stroke="{PINK}" stroke-width="1.5" stroke-dasharray="20 170" stroke-linecap="round">'
        f'<animateTransform attributeName="transform" type="rotate" values="360;0" dur="3s" repeatCount="indefinite"/></circle>'
        f'<circle r="5" fill="{VIOLET}"><animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite"/></circle>'
        f'<text y="72" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}" letter-spacing="2">LINK OK</text></g>'
    )
    parts.append(f'<text x="530" y="74" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="2">LANGUAGES</text>')
    for i, (name, (size, color)) in enumerate(top):
        y = 96 + i * 32
        pct = size / total
        bw = 300 * pct
        begin = 0.6 + i * 0.2
        parts.append(
            f'<text x="530" y="{y + 4}" font-family="{FONT}" font-size="12" fill="{TEXT}">{name}</text>'
            f'<text x="860" y="{y + 4}" text-anchor="end" font-family="{FONT}" font-size="11" fill="{MUTED}">{pct * 100:.1f}%</text>'
            f'<rect x="530" y="{y + 10}" width="330" height="5" rx="2.5" fill="{VIOLET}" fill-opacity="0.12"/>'
            f'<rect x="530" y="{y + 10}" width="0" height="5" rx="2.5" fill="{color}" filter="url(#glow)">'
            f'<animate attributeName="width" values="0;{max(bw * 330 / 300, 3):.1f}" begin="{begin:.1f}s" dur="1.2s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1" keyTimes="0;1"/></rect>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="GitHub telemetry">'
        f"{defs()}{frame(w, h, 'TELEMETRY')}{''.join(parts)}</svg>"
    )


# ---------------------------------------------------------------- Starfield de contribuciones


def starfield(u):
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    cols = len(weeks)
    cell = 16
    left, top = 34, 62
    w = left * 2 + cols * cell
    h = top + 7 * cell + 46
    counts = [d["contributionCount"] for wk in weeks for d in wk["contributionDays"]]
    peak = max(counts) if counts else 1
    rnd = random.Random(42)
    stars = []
    beam_dur = 6.0
    for x, wk in enumerate(weeks):
        for y, d in enumerate(wk["contributionDays"]):
            c = d["contributionCount"]
            cx = left + x * cell + cell / 2 + rnd.uniform(-2.5, 2.5)
            cy = top + y * cell + cell / 2 + rnd.uniform(-2.5, 2.5)
            if c == 0:
                stars.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0.9" fill="{MUTED}" fill-opacity="0.35"/>')
                continue
            level = math.sqrt(c / peak)
            r = 1.6 + level * 3.6
            color = PINK if level > 0.75 else CYAN if level > 0.4 else VIOLET
            # el haz pasa por esta columna en este momento
            t = beam_dur * (cx - left) / (w - 2 * left)
            stars.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}" filter="url(#glow)" opacity="{0.45 + level * 0.4:.2f}">'
                f'<animate attributeName="opacity" values="{0.45 + level * 0.4:.2f};1;{0.45 + level * 0.4:.2f}" begin="{t:.2f}s" dur="{beam_dur}s" keyTimes="0;0.06;1" repeatCount="indefinite"/>'
                f'<animate attributeName="r" values="{r:.1f};{r * 1.6:.1f};{r:.1f}" begin="{t:.2f}s" dur="{beam_dur}s" keyTimes="0;0.06;1" repeatCount="indefinite"/></circle>'
            )
    beam = (
        f'<clipPath id="field"><rect x="{left - 8}" y="{top - 8}" width="{w - 2 * left + 16}" height="{7 * cell + 16}"/></clipPath>'
        f'<g clip-path="url(#field)"><rect x="{left - 60}" y="{top - 8}" width="60" height="{7 * cell + 16}" fill="url(#beam)">'
        f'<animate attributeName="x" values="{left - 60};{w - left}" dur="{beam_dur}s" repeatCount="indefinite"/></rect></g>'
    )
    label = (
        f'<text x="{left}" y="{h - 16}" font-family="{FONT}" font-size="12" fill="{MUTED}" letter-spacing="2">'
        f"{total:,} CONTRIBUTIONS IN THE LAST YEAR · EACH STAR IS A DAY</text>"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Contribution starfield">'
        f"{defs()}{frame(w, h, 'CONTRIBUTION STARFIELD')}{''.join(stars)}{beam}{label}</svg>"
    )


if __name__ == "__main__":
    (OUT / "engine-room.svg").write_text(engine_room(), encoding="utf-8")
    user = github()
    (OUT / "telemetry.svg").write_text(telemetry(user), encoding="utf-8")
    (OUT / "starfield.svg").write_text(starfield(user), encoding="utf-8")
    print("ok", OUT)
