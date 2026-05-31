"""
generate_icons.py
Erstellt assets/app.ico mit ALLEN Windows-Standard-Groessen:
  256, 128, 64, 48, 40, 32, 24, 20, 16 px

Technik:
  - Supersampling 8x: jeder Frame 8x groesser rendern, dann LANCZOS
  - Stroke auf Text: macht "vt" bei kleinen Groessen scharf + fett
  - Alle Taskleisten-Groessen enthalten (24, 40 px = Windows-Standard)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Alle Windows-Standard-Groessen inkl. Taskleisten-spezifische
SIZES = [256, 128, 64, 48, 40, 32, 24, 20, 16]
SS    = 8   # Supersample-Faktor (8x fuer maximale Schaerfe)

NAVY  = (13,  31,  53,  255)   # #0d1f35
BLUE  = (30,  95, 212,  255)   # #1e5fd4
WHITE = (255, 255, 255, 255)

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(OUT_DIR, exist_ok=True)

FONT_PATHS = [
    r"C:\Windows\Fonts\segoeuib.ttf",   # Segoe UI Bold
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]


def _load_font(px: int):
    for p in FONT_PATHS:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, px)
            except Exception:
                continue
    return None


def make_frame(size: int) -> Image.Image:
    rs = size * SS   # Render-Groesse (z.B. 256 × 8 = 2048 px)
    r  = rs // 7     # Ecken-Radius

    # ── Hintergrund mit abgerundeten Ecken ──────────────────────────
    base = Image.new('RGBA', (rs, rs), (0, 0, 0, 0))
    bd   = ImageDraw.Draw(base)
    bd.rounded_rectangle([(0, 0), (rs - 1, rs - 1)], radius=r, fill=NAVY)

    # ── Blauer Streifen unten (abgerundet unten) ─────────────────────
    bar_h = max(rs // 10, 8)
    bar   = Image.new('RGBA', (rs, rs), (0, 0, 0, 0))
    bard  = ImageDraw.Draw(bar)
    bard.rounded_rectangle(
        [(0, rs - bar_h), (rs - 1, rs - 1)],
        radius=r, fill=BLUE,
    )
    base = Image.alpha_composite(base, bar)

    # ── "vt"-Text mit Stroke (dicker Rand = scharf bei kleinen Groessen)
    draw      = ImageDraw.Draw(base)
    font_px   = int(rs * 0.48)
    font      = _load_font(font_px)
    text      = "vt"
    stroke_w  = max(1, rs // 80)   # Stroke-Breite proportional zur Groesse

    if font:
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
        tw   = bbox[2] - bbox[0]
        th   = bbox[3] - bbox[1]
        x    = (rs - tw) / 2 - bbox[0]
        y    = (rs - bar_h - th) / 2 - bbox[1] - rs * 0.02
        draw.text(
            (x, y), text,
            font=font, fill=WHITE,
            stroke_width=stroke_w, stroke_fill=WHITE,
        )
    else:
        draw.text((rs // 4, rs // 4), text, fill=WHITE)

    # ── Supersampling: 8x → Zielgroesse ─────────────────────────────
    return base.resize((size, size), Image.LANCZOS)


def main():
    print(f"Supersampling {SS}x – rendere {len(SIZES)} Groessen ...")
    frames = [make_frame(s) for s in SIZES]

    ico_path = os.path.join(OUT_DIR, 'app.ico')
    frames[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in SIZES],
        append_images=frames[1:],
    )
    print(f"OK  app.ico  ({', '.join(str(s) for s in SIZES)} px)")

    preview = os.path.join(OUT_DIR, 'icon_preview.png')
    frames[0].save(preview)
    print(f"OK  Vorschau: {preview}")


if __name__ == '__main__':
    main()
