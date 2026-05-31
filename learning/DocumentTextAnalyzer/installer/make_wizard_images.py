"""
make_wizard_images.py
Erstellt die Inno-Setup-Wizard-Bilder für das VT-Branding.
Ausführen: python installer/make_wizard_images.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")

NAVY_DARK   = (13,  31,  53)   # #0d1f35
NAVY_MED    = (16,  42,  71)   # #102a47
BLUE_ACCENT = (30,  95, 212)   # #1e5fd4
MUTED       = (107, 140, 170)  # #6b8caa
LIGHT_MUTED = (160, 188, 208)  # #a0bcd0
WHITE       = (255, 255, 255)


def load_font(path, size, fallback_size=None):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


SEG_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
SEG_REG  = "C:/Windows/Fonts/segoeui.ttf"


# ── 1. Kleines Wizard-Bild (55×58 px) – erscheint oben rechts ─────────────
def make_small():
    img  = Image.new("RGB", (55, 58), NAVY_DARK)
    draw = ImageDraw.Draw(img)

    # Linker Akzentstreifen
    draw.rectangle([0, 0, 3, 57], fill=BLUE_ACCENT)

    fnt_big = load_font(SEG_BOLD, 18)
    fnt_sm  = load_font(SEG_REG,   8)

    draw.text((10, 12), "VT",   font=fnt_big, fill=WHITE)
    draw.rectangle([8, 34, 47, 35], fill=BLUE_ACCENT)
    draw.text((8,  38), "v1.0", font=fnt_sm,  fill=MUTED)

    out = os.path.join(ASSETS, "wizard_small.bmp")
    img.save(out, "BMP")
    print(f"  OK  wizard_small.bmp  ({img.size})")


# ── 2. Großes Banner (164×314 px) – linke Seite Willkommen/Abschluss ──────
def make_banner():
    banner = Image.new("RGB", (164, 314), NAVY_DARK)
    draw   = ImageDraw.Draw(banner)

    # Leichter Farbverlauf (oben dunkler)
    for y in range(230):
        t   = y / 230
        r   = int(NAVY_DARK[0] + t * (NAVY_MED[0] - NAVY_DARK[0]))
        g   = int(NAVY_DARK[1] + t * (NAVY_MED[1] - NAVY_DARK[1]))
        b   = int(NAVY_DARK[2] + t * (NAVY_MED[2] - NAVY_DARK[2]))
        draw.line([(0, y), (163, y)], fill=(r, g, b))

    # Rechter Akzentstreifen
    draw.rectangle([161, 0, 163, 313], fill=BLUE_ACCENT)

    # Logo einfügen (invertiert → weiß)
    logo_path = os.path.join(ASSETS, "logo.png")
    if os.path.isfile(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            r, g, b, a = logo.split()
            logo_inv = Image.merge("RGBA", (
                r.point(lambda v: 255 - v),
                g.point(lambda v: 255 - v),
                b.point(lambda v: 255 - v), a,
            ))
            lw, lh = logo_inv.size
            sc = min(130 / lw, 40 / lh)
            logo_sm = logo_inv.resize((int(lw * sc), int(lh * sc)), Image.LANCZOS)
            lx = (164 - logo_sm.width) // 2
            banner.paste(logo_sm, (lx, 22), logo_sm)
        except Exception as e:
            print(f"  ⚠  Logo: {e}")

    fnt_big = load_font(SEG_BOLD, 20)
    fnt_med = load_font(SEG_BOLD, 11)
    fnt_sml = load_font(SEG_REG,   9)

    draw.text((14,  78), "VT",         font=fnt_big, fill=WHITE)
    draw.text((14, 104), "Document",   font=fnt_med, fill=LIGHT_MUTED)
    draw.text((14, 118), "Text",       font=fnt_med, fill=LIGHT_MUTED)
    draw.text((14, 132), "Converter",  font=fnt_med, fill=LIGHT_MUTED)

    # Trennlinie
    draw.rectangle([14, 156, 148, 158], fill=BLUE_ACCENT)

    draw.text((14, 163), "Version 1.0",       font=fnt_sml, fill=MUTED)
    draw.text((14, 175), "vt-solutions GmbH", font=fnt_sml, fill=MUTED)

    # Unterer Info-Bereich
    draw.rectangle([0, 258, 163, 313], fill=NAVY_MED)
    draw.line([(0, 258), (163, 258)], fill=BLUE_ACCENT)
    draw.text((14, 266), "Professionelle",  font=fnt_sml, fill=(138, 160, 188))
    draw.text((14, 278), "Texterkennung",   font=fnt_sml, fill=(138, 160, 188))
    draw.text((14, 290), "für Windows",     font=fnt_sml, fill=(138, 160, 188))

    out = os.path.join(ASSETS, "wizard_banner.bmp")
    banner.save(out, "BMP")
    print(f"  OK  wizard_banner.bmp  ({banner.size})")


if __name__ == "__main__":
    print("Wizard-Bilder werden erstellt ...")
    make_small()
    make_banner()
    print("Fertig.")
