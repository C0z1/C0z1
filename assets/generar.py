"""Genera las animaciones SVG del perfil (encabezado y separador). Uso: python assets/generar.py"""

import random
from pathlib import Path

AQUI = Path(__file__).parent
random.seed(7)
W, H = 1200, 300


def estrellas(n):
    out = []
    for _ in range(n):
        x, y = random.uniform(0, W), random.uniform(0, H)
        r = random.choice([0.6, 0.8, 1, 1.2, 1.6])
        dur, begin = round(random.uniform(1.5, 5), 2), round(random.uniform(0, 5), 2)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#e8e6ff">'
            f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


CX, CY = 930, 150


def orbita(rx, ry, dur, radio, color, reversa=False):
    s = 0 if reversa else 1
    path = f"M {CX - rx},{CY} a {rx},{ry} 0 1,{s} {2 * rx},0 a {rx},{ry} 0 1,{s} {-2 * rx},0"
    return (
        f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="#a78bfa" '
        f'stroke-opacity="0.22" stroke-dasharray="3 6"/>'
        f'<circle r="{radio}" fill="{color}" filter="url(#glow)">'
        f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/></circle>'
    )


orbitas = (
    orbita(80, 26, 6, 4, "#7dd3fc")
    + orbita(140, 46, 11, 6, "#c4b5fd", True)
    + orbita(210, 70, 19, 5, "#f0abfc")
    + orbita(270, 92, 29, 3.5, "#93c5fd", True)
)

cometa = (
    '<g opacity="0.9"><line x1="0" y1="0" x2="-90" y2="-28" stroke="url(#tail)" '
    'stroke-width="2" stroke-linecap="round"/><circle r="2.4" fill="#fff"/>'
    '<animateMotion dur="7s" begin="1s" repeatCount="indefinite" path="M -100,40 L 1300,470"/></g>'
)

encabezado = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Felix Tavera - software, AI, physics, Linux">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05010f"/><stop offset="0.55" stop-color="#140a33"/><stop offset="1" stop-color="#2a1d6e"/></linearGradient>
<radialGradient id="neb" cx="0.78" cy="0.5" r="0.5"><stop offset="0" stop-color="#7c3aed" stop-opacity="0.35"/><stop offset="1" stop-color="#7c3aed" stop-opacity="0"/></radialGradient>
<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff7d6"/><stop offset="0.45" stop-color="#fbbf24"/><stop offset="1" stop-color="#f59e0b" stop-opacity="0"/></radialGradient>
<linearGradient id="tail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0.9"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>
<linearGradient id="txt" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox"><stop offset="0" stop-color="#e8e6ff"/><stop offset="0.5" stop-color="#c4b5fd"/><stop offset="1" stop-color="#7dd3fc"/>
<animateTransform attributeName="gradientTransform" type="translate" values="-0.5 0;0.5 0;-0.5 0" dur="8s" repeatCount="indefinite"/></linearGradient>
<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#neb)"><animate attributeName="opacity" values="0.6;1;0.6" dur="9s" repeatCount="indefinite"/></rect>
{estrellas(110)}
{cometa}
{orbitas}
<circle cx="{CX}" cy="{CY}" r="34" fill="url(#sun)"><animate attributeName="r" values="32;37;32" dur="4s" repeatCount="indefinite"/></circle>
<g font-family="Fira Code, JetBrains Mono, Consolas, monospace">
<text x="70" y="110" font-size="15" fill="#a78bfa" letter-spacing="4">felix@nube:~$ whoami</text>
<text x="68" y="172" font-size="58" font-weight="700" fill="url(#txt)" font-family="Segoe UI, Helvetica, Arial, sans-serif">Félix Tavera</text>
<text x="72" y="212" font-size="17" fill="#cbd5e1" letter-spacing="2">software · AI · physics · Linux</text>
<rect x="72" y="232" width="10" height="18" fill="#a78bfa"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>
</g>
</svg>
"""

separador = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 24" width="1200" height="24">
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="#a78bfa" stop-opacity="0"/><stop offset="0.5" stop-color="#a78bfa" stop-opacity="0.5"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>
<linearGradient id="t" x1="0" x2="1"><stop offset="0" stop-color="#7dd3fc" stop-opacity="0"/><stop offset="1" stop-color="#ffffff"/></linearGradient></defs>
<rect x="0" y="11.5" width="1200" height="1" fill="url(#l)"/>
<g><rect x="-160" y="10.5" width="160" height="3" rx="1.5" fill="url(#t)"/><circle cx="0" cy="12" r="3" fill="#fff"/>
<animateTransform attributeName="transform" type="translate" values="0 0;1400 0" dur="4.5s" repeatCount="indefinite"/></g>
</svg>
"""

(AQUI / "header.svg").write_text(encabezado, encoding="utf-8")
(AQUI / "divider.svg").write_text(separador, encoding="utf-8")
print("ok")
