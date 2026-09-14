"""Shared palette and SVG primitives.

Every graphic on the profile is drawn here rather than fetched from a
third-party badge service, so nothing can rate-limit or disappear.

Glyphs are positioned one at a time with an explicit x coordinate. That
removes the dependency on the viewer's default monospace advance width:
the grid holds even if the fallback font is narrower than JetBrains Mono.
"""

# Ice and open-water palette, taken from the sea-ice work rather than a
# generic terminal green. Amber is reserved for risk/attention only.
ABYSS = "#0B1E2D"  # deep water / dark-mode ground
OCEAN = "#1B4965"  # open water
MELT = "#5FA8D3"  # meltwater, primary accent
ICE = "#9AD1D4"  # consolidated ice
RIME = "#E8F1F2"  # fast ice, brightest value
AMBER = "#F2A65A"  # risk, attention, RIO limits
SLATE = "#6E8CA0"  # muted metadata

MONO = "ui-monospace, 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace"

# Character ramp, quiet to loud. Reused by the hero field and the year strip
# so the two read as the same visual language.
RAMP = " .:+*#@"

CELL_W = 8.4
CELL_H = 15.0


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def glyph_row(chars, x0, y, fill=None, size=13.0, cell=CELL_W, opacity=None,
              cls=None):
    """Render one row of monospaced text as individually positioned glyphs."""
    xs = " ".join(f"{x0 + i * cell:.2f}" for i in range(len(chars)))
    op = f' opacity="{opacity}"' if opacity is not None else ""
    paint = f' class="{cls}"' if cls else f' fill="{fill}"'
    return (
        f'<text x="{xs}" y="{y:.2f}"{paint} font-family="{MONO}" '
        f'font-size="{size}"{op} xml:space="preserve">{esc("".join(chars))}</text>'
    )


# Concentration ramp, quiet to loud, in both schemes. GitHub serves the README
# on a light or a dark ground depending on the viewer, so a fixed fill would
# make one end of the ramp invisible. Index 0 is never drawn (open water).
SHADES_LIGHT = ["", "#CBDFE9", "#A3C8DA", "#75A8C6", "#4B85A9", "#2C6688", "#164A66"]
SHADES_DARK = ["", "#1B4965", "#2E6285", "#4A86A8", "#74AFC9", "#A8D5DC", "#E8F1F2"]


def shade_style() -> str:
    light = "".join(f".s{i}{{fill:{c}}}" for i, c in enumerate(SHADES_LIGHT) if c)
    dark = "".join(f".s{i}{{fill:{c}}}" for i, c in enumerate(SHADES_DARK) if c)
    return light + "@media (prefers-color-scheme: dark){" + dark + "}"


def svg_open(w, h, title, extra_style=""):
    """Root element. The <style> block inside an SVG loaded as an <img> still
    honours prefers-color-scheme, which is the only theming lever left once
    GitHub has stripped CSS from the README itself."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
        "<style>"
        f".bg{{fill:{RIME}}}.fg{{fill:{ABYSS}}}.mut{{fill:{SLATE}}}"
        "@media (prefers-color-scheme: dark){"
        f".bg{{fill:{ABYSS}}}.fg{{fill:{RIME}}}}}"
        f"{extra_style}"
        "</style>"
    )


SVG_CLOSE = "</svg>"
