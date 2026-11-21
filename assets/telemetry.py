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
    """Telemetría de vuelo: datos tipo HUD, la curva de contribuciones por semana que se dibuja
    sola y los lenguajes como planetas orbitando un núcleo (tamaño = porcentaje)."""
    w, h = 900, 320
    repos = u["repositories"]["totalCount"]
    cc = u["contributionsCollection"]
    commits = cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    contrib = cc["contributionCalendar"]["totalContributions"]
    weeks = cc["contributionCalendar"]["weeks"]
    per_week = [sum(d["contributionCount"] for d in wk["contributionDays"]) for wk in weeks]
    active = sum(1 for wk in weeks for d in wk["contributionDays"] if d["contributionCount"] > 0)
    streak = best = 0
    for wk in weeks:
        for d in wk["contributionDays"]:
            streak = streak + 1 if d["contributionCount"] else 0
            best = max(best, streak)

    langs = {}
    for n in u["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            name = e["node"]["name"]
            if name in SKIP_LANGS:
                continue
            langs.setdefault(name, [0, e["node"]["color"] or VIOLET])
            langs[name][0] += e["size"]
    total = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]

    parts = []
    # ---- HUD de datos (izquierda)
    hud = [
        ("COMMITS / YR", f"{commits:,}"),
        ("CONTRIBUTIONS", f"{contrib:,}"),
        ("ACTIVE DAYS", f"{active}"),
        ("BEST STREAK", f"{best} d"),
        ("PUBLIC REPOS", f"{repos}"),
    ]
    for i, (label, value) in enumerate(hud):
        y = 74 + i * 30
        b = 0.15 + i * 0.18
        parts.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1" begin="{b:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<text x="34" y="{y}" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="2">{label}</text>'
            f'<line x1="150" y1="{y - 4}" x2="230" y2="{y - 4}" stroke="{VIOLET}" stroke-opacity="0.25" stroke-dasharray="2 4"/>'
            f'<text x="330" y="{y}" text-anchor="end" font-family="{FONT}" font-size="15" font-weight="700" fill="{TEXT}" filter="url(#glow)">{value}</text></g>'
        )

    # ---- curva de contribuciones por semana (abajo izquierda), se dibuja sola
    gx, gy, gw, gh = 34, 236, 300, 56
    peak = max(per_week) or 1
    n = len(per_week)
    pts = [(gx + gw * i / max(n - 1, 1), gy + gh - gh * v / peak) for i, v in enumerate(per_week)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{gx},{gy + gh} " + line + f" {gx + gw},{gy + gh}"
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(n - 1)) + 10
    parts.append(
        f'<text x="{gx}" y="{gy - 10}" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="2">WEEKLY SIGNAL · 12 MONTHS</text>'
        f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy + gh}" stroke="{VIOLET}" stroke-opacity="0.25"/>'
        f'<polygon points="{area}" fill="{CYAN}" fill-opacity="0"><animate attributeName="fill-opacity" values="0;0.12" begin="2.2s" dur="1s" fill="freeze"/></polygon>'
        f'<polyline points="{line}" fill="none" stroke="{CYAN}" stroke-width="1.8" stroke-linejoin="round" filter="url(#glow)" '
        f'stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">'
        f'<animate attributeName="stroke-dashoffset" values="{length:.0f};0" begin="0.8s" dur="2s" fill="freeze"/></polyline>'
        f'<circle r="3" fill="{PINK}" filter="url(#glow)"><animateMotion dur="6s" begin="3s" repeatCount="indefinite" path="M {line.replace(" ", " L ")}"/></circle>'
    )

    # ---- sistema de lenguajes (derecha): planetas que orbitan el núcleo
    cx, cy = 640, 178
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="26" fill="{VIOLET}" fill-opacity="0.12" stroke="{VIOLET}" stroke-opacity="0.6">'
        f'<animate attributeName="r" values="24;28;24" dur="4s" repeatCount="indefinite"/></circle>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{TEXT}" letter-spacing="1">CODE</text>'
        f'<text x="{cx}" y="64" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}" letter-spacing="2">LANGUAGE SYSTEM</text>'
    )
    rnd = random.Random(3)
    for i, (name, (size, color)) in enumerate(top):
        pct = size / total
        rx, ry = 92 + i * 34, 38 + i * 12
        pr = 4 + 12 * math.sqrt(pct)
        dur = 9 + i * 5
        start = rnd.uniform(0, 1)
        path = f"M {cx + rx},{cy} A {rx},{ry} 0 1,1 {cx - rx},{cy} A {rx},{ry} 0 1,1 {cx + rx},{cy}"
        parts.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{color}" stroke-opacity="0.22" stroke-dasharray="2 5"/>'
            f'<g><animateMotion dur="{dur}s" begin="-{start * dur:.1f}s" repeatCount="indefinite" path="{path}"/>'
            f'<circle r="{pr:.1f}" fill="{color}" filter="url(#glow)"/>'
            f'<text x="{pr + 5:.1f}" y="4" font-family="{FONT}" font-size="11" fill="{TEXT}">{name} {pct * 100:.0f}%</text></g>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="GitHub telemetry">'
        f"{defs()}{frame(w, h, 'FLIGHT TELEMETRY')}{''.join(parts)}</svg>"
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
