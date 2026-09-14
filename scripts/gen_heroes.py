"""Alternative hero graphics.

Each writes a standalone SVG. To use one, copy it over hero.svg, or point the
README's first image at the file directly.

    python scripts/gen_heroes.py            # all four
    python scripts/gen_heroes.py residual   # just one

All four share the palette and the glyph-placement rules in theme.py, so any of
them sits correctly next to the headings and stat panels.
"""

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from theme import (  # noqa: E402
    AMBER, ICE, MELT, MONO, OCEAN, RAMP, SLATE, SVG_CLOSE, esc, glyph_row,
    shade_style, svg_open,
)

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gen_hero import concentration, fbm  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent

NAME = "ARMAN"
W = 720


def name_block(tagline, y=17):
    return (
        f'<text x="4" y="{y}" class="fg" font-family="{MONO}" font-size="16" '
        f'font-weight="700" letter-spacing="3.5">{NAME}</text>'
        f'<text x="{4 + 7 * 13.5:.0f}" y="{y}" class="mut" font-family="{MONO}" '
        f'font-size="11">{esc(tagline)}</text>'
    )


def axis_label(x, y, text, size=10, fill=None, cls="mut", anchor="start"):
    paint = f'fill="{fill}"' if fill else f'class="{cls}"'
    return (f'<text x="{x:.1f}" y="{y:.1f}" {paint} font-family="{MONO}" '
            f'font-size="{size}" text-anchor="{anchor}">{esc(text)}</text>')


# ---------------------------------------------------------------- firing order

def firing_order() -> str:
    """Four cylinders pulsing in 1-3-4-2, the firing order of an inline four.

    One full cycle is 720 degrees of crank rotation, so each cylinder fires
    once every two revolutions — the timing below is that, not decoration.
    """
    h = 190
    order = [1, 3, 4, 2]
    cycle = 3.2  # seconds per 720 degrees
    bore_w, bore_h, gap = 116, 74, 22
    x0 = 6
    top = 46

    p = [svg_open(W, h, "Inline-four firing order, 1-3-4-2")]
    p.append(name_block("engine health monitoring, in real time"))

    for i in range(4):
        cyl = i + 1
        x = x0 + i * (bore_w + gap)
        phase = order.index(cyl) * (cycle / 4)
        p.append(
            f'<rect x="{x}" y="{top}" width="{bore_w}" height="{bore_h}" rx="3" '
            f'fill="none" stroke="{MELT}" stroke-width="1.2" opacity="0.5"/>'
        )
        # The power stroke: a brief amber flood, then decay.
        p.append(
            f'<rect x="{x + 1}" y="{top + 1}" width="{bore_w - 2}" '
            f'height="{bore_h - 2}" rx="2" fill="{AMBER}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.85;0.12;0" '
            f'keyTimes="0;0.06;0.3;1" dur="{cycle}s" begin="{phase:.2f}s" '
            f'repeatCount="indefinite"/></rect>'
        )
        # Piston crown, dropping on the stroke it fires.
        p.append(
            f'<rect x="{x + 14}" y="{top + 16}" width="{bore_w - 28}" height="9" '
            f'rx="2" fill="{MELT}">'
            f'<animate attributeName="y" values="{top + 16};{top + 48};{top + 16}" '
            f'keyTimes="0;0.25;1" dur="{cycle}s" begin="{phase:.2f}s" '
            f'repeatCount="indefinite"/></rect>'
        )
        p.append(axis_label(x + bore_w / 2, top + bore_h - 8, f"cyl {cyl}",
                            size=11, anchor="middle"))

    # Crank-angle scale, so the graphic reads as instrumentation.
    base = top + bore_h + 26
    p.append(f'<line x1="6" y1="{base}" x2="{W - 6}" y2="{base}" stroke="{MELT}" '
             f'stroke-width="1" opacity="0.35"/>')
    for i in range(5):
        x = 6 + i * (W - 12) / 4
        p.append(f'<line x1="{x:.1f}" y1="{base - 4}" x2="{x:.1f}" y2="{base + 4}" '
                 f'stroke="{MELT}" stroke-width="1" opacity="0.5"/>')
        anchor = "start" if i == 0 else "end" if i == 4 else "middle"
        p.append(axis_label(x, base + 17, f"{i * 180}°", anchor=anchor))
    p.append(
        f'<circle cy="{base}" r="3.5" fill="{AMBER}">'
        f'<animate attributeName="cx" from="6" to="{W - 6}" dur="{cycle}s" '
        f'repeatCount="indefinite"/></circle>'
    )
    p.append(axis_label(W - 6, 30, "firing order 1-3-4-2", anchor="end"))
    p.append(SVG_CLOSE)
    return "".join(p)


# ------------------------------------------------------------------ RUL curve

def rul_curve() -> str:
    """Health descending toward a limit, with an uncertainty band that widens
    the further out the prediction goes. The widening is the honest part."""
    h = 210
    left, right = 44, W - 96
    top, bottom = 44, 158
    n = 120

    def health(t):  # t in 0..1
        return 1.0 - 0.18 * t - 0.82 * t ** 3.1

    def spread(t):
        return 0.055 + 0.30 * t ** 2.2

    p = [svg_open(W, h, "Remaining useful life, with widening uncertainty")]
    p.append(name_block("predicting when, not just whether"))

    def px(t):
        return left + t * (right - left)

    def py(v):
        return bottom - max(0.0, min(1.0, v)) * (bottom - top)

    upper = [(px(i / n), py(health(i / n) + spread(i / n))) for i in range(n + 1)]
    lower = [(px(i / n), py(health(i / n) - spread(i / n))) for i in range(n + 1)]
    band = ("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in upper) + " L "
            + " L ".join(f"{x:.1f} {y:.1f}" for x, y in reversed(lower)) + " Z")
    p.append(f'<path d="{band}" fill="{MELT}" opacity="0.18"/>')

    mid = "M " + " L ".join(f"{px(i / n):.1f} {py(health(i / n)):.1f}"
                            for i in range(n + 1))
    p.append(f'<path d="{mid}" fill="none" stroke="{MELT}" stroke-width="2"/>')

    # Failure threshold.
    thr = 0.3
    p.append(f'<line x1="{left}" y1="{py(thr):.1f}" x2="{right}" y2="{py(thr):.1f}" '
             f'stroke="{AMBER}" stroke-width="1.3" stroke-dasharray="5 4"/>')
    p.append(axis_label(right + 8, py(thr) + 4, "limit", fill=AMBER))

    # Where the mean curve crosses: the number the whole thing exists to produce.
    cross = next(i / n for i in range(n + 1) if health(i / n) <= thr)
    p.append(f'<line x1="{px(cross):.1f}" y1="{top}" x2="{px(cross):.1f}" '
             f'y2="{bottom}" stroke="{AMBER}" stroke-width="1" opacity="0.4"/>')
    p.append(axis_label(px(cross), top - 8, "RUL", size=11, fill=AMBER,
                        anchor="middle"))

    p.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
             f'stroke="{MELT}" stroke-width="1" opacity="0.4"/>')
    p.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" '
             f'stroke="{MELT}" stroke-width="1" opacity="0.4"/>')
    p.append(axis_label(left - 8, top + 6, "1.0", anchor="end"))
    p.append(axis_label(left - 8, bottom + 4, "0", anchor="end"))
    p.append(axis_label(left, bottom + 18, "engine hours →"))
    p.append(axis_label(right + 8, py(0.72) + 4, "health", cls="mut"))

    p.append(
        f'<circle r="4" fill="{AMBER}">'
        f'<animateMotion dur="9s" repeatCount="indefinite" path="{mid}"/></circle>'
    )
    p.append(SVG_CLOSE)
    return "".join(p)


# -------------------------------------------------------------- residual trace

def residual_trace() -> str:
    """Measured against modelled, with the gap between them filled. A fault is
    injected partway across and the residual blows out — which is the whole of
    residual-based diagnosis in one picture."""
    h = 210
    left, right = 44, W - 86
    mid_y, amp = 96, 34
    n = 260
    fault_at = 0.58

    def modelled(t):
        return math.sin(t * 21.0) * 0.5 + math.sin(t * 6.4 + 0.8) * 0.32

    def measured(t):
        base = modelled(t) + (fbm(t * 42, 3.0, seed=41) - 0.5) * 0.14
        if t > fault_at:
            g = min(1.0, (t - fault_at) / 0.22)
            base += g * (0.42 * math.sin(t * 96.0) + 0.16)
        return base

    p = [svg_open(W, h, "Measured against modelled, with the residual filled")]
    p.append(name_block("diagnosis from the gap, not the signal"))

    def px(t):
        return left + t * (right - left)

    def py(v):
        return mid_y - v * amp

    mod_pts = [(px(i / n), py(modelled(i / n))) for i in range(n + 1)]
    mea_pts = [(px(i / n), py(measured(i / n))) for i in range(n + 1)]

    fill = ("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in mea_pts) + " L "
            + " L ".join(f"{x:.1f} {y:.1f}" for x, y in reversed(mod_pts)) + " Z")
    p.append(f'<path d="{fill}" fill="{AMBER}" opacity="0.30"/>')

    p.append('<path d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in mod_pts)
             + f'" fill="none" stroke="{MELT}" stroke-width="1.6" opacity="0.9"/>')
    p.append('<path d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in mea_pts)
             + f'" fill="none" stroke="{ICE}" stroke-width="1.4"/>')

    fx = px(fault_at)
    p.append(f'<line x1="{fx:.1f}" y1="34" x2="{fx:.1f}" y2="{mid_y + amp + 22}" '
             f'stroke="{AMBER}" stroke-width="1" stroke-dasharray="3 3" opacity="0.8"/>')
    p.append(axis_label(fx + 6, 44, "fault injected", size=10.5, fill=AMBER))

    # Residual magnitude below, against a detection threshold.
    r_base = 186
    p.append(f'<line x1="{left}" y1="{r_base}" x2="{right}" y2="{r_base}" '
             f'stroke="{MELT}" stroke-width="1" opacity="0.35"/>')
    thr_y = r_base - 15
    p.append(f'<line x1="{left}" y1="{thr_y}" x2="{right}" y2="{thr_y}" '
             f'stroke="{AMBER}" stroke-width="1" stroke-dasharray="4 4" opacity="0.7"/>')
    for i in range(n + 1):
        t = i / n
        r = abs(measured(t) - modelled(t))
        bar = min(34, r * 42)
        if bar < 0.6:
            continue
        x = px(t)
        colour = AMBER if bar > 15 else MELT
        p.append(f'<line x1="{x:.1f}" y1="{r_base}" x2="{x:.1f}" '
                 f'y2="{r_base - bar:.1f}" stroke="{colour}" stroke-width="1.1" '
                 f'opacity="0.85"/>')
    p.append(axis_label(right + 8, thr_y + 4, "thresh", fill=AMBER))
    p.append(axis_label(left, r_base + 16, "|residual|"))
    p.append(axis_label(right + 8, py(0.0) + 4, "model", fill=MELT))
    p.append(axis_label(right + 8, py(0.0) + 17, "measured", fill=ICE))
    p.append(SVG_CLOSE)
    return "".join(p)


# ------------------------------------------------------------------ split field

def split_field() -> str:
    """Ice on the left, engine trace on the right, one rule between them —
    two problems with the same shape."""
    h = 212
    cols, rows = 38, 9
    cell_w, cell_h = 8.4, 15.0
    p = [svg_open(W, h, "Ice field and engine trace, side by side",
                  extra_style=shade_style())]
    p.append(name_block("two domains, one problem shape"))

    for row in range(rows):
        y = 48 + row * cell_h
        shades, chars = [], []
        for col in range(cols):
            c = concentration(col, int(row * 21 / rows))
            idx = min(len(RAMP) - 1, int((c ** 1.45) * len(RAMP)))
            shades.append(idx)
            chars.append(RAMP[idx])
        start = 0
        for i in range(1, cols + 1):
            if i == cols or shades[i] != shades[start]:
                if shades[start]:
                    p.append(glyph_row(chars[start:i], 6 + start * cell_w, y,
                                       size=13, cls=f"s{shades[start]}"))
                start = i

    divide = 6 + cols * cell_w + 18
    p.append(f'<line x1="{divide:.1f}" y1="40" x2="{divide:.1f}" y2="{h - 26}" '
             f'stroke="{MELT}" stroke-width="1" opacity="0.4"/>')

    rl, rr = divide + 24, W - 12
    mid_y, amp = 108, 30
    n = 200
    pts, fpts = [], []
    for i in range(n + 1):
        t = i / n
        x = rl + t * (rr - rl)
        base = math.sin(t * 11) * 0.5 + math.sin(t * 3.6 + 1.1) * 0.28
        pts.append((x, mid_y - base * amp))
        f = base + (0.5 * math.sin(t * 26) + 0.3 if t > 0.62 else 0)
        fpts.append((x, mid_y - f * amp))
    p.append('<path d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
             + f'" fill="none" stroke="{MELT}" stroke-width="1.5" opacity="0.85"/>')
    p.append('<path d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in fpts)
             + f'" fill="none" stroke="{AMBER}" stroke-width="1.3"/>')

    p.append(axis_label(6, h - 10, "where can the ship go?"))
    p.append(axis_label(rl, h - 10, "can the engine finish?"))
    p.append(SVG_CLOSE)
    return "".join(p)


BUILDERS = {
    "firing": firing_order,
    "rul": rul_curve,
    "residual": residual_trace,
    "split": split_field,
}


def main() -> None:
    wanted = sys.argv[1:] or list(BUILDERS)
    for key in wanted:
        if key not in BUILDERS:
            raise SystemExit(f"unknown hero {key!r}; pick from {list(BUILDERS)}")
        path = OUT / f"hero-{key}.svg"
        path.write_text(BUILDERS[key](), encoding="utf-8")
        print(f"wrote {path.name} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
