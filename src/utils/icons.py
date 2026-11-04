"""
Iconos dibujados con Pillow para los botones.

Tk en Windows muestra los emojis en blanco y negro y con tamaños irregulares,
así que los iconos se dibujan a mano: a 4x de tamaño y luego se reducen para
que los bordes queden suaves.
"""

from typing import Dict, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageTk

_SCALE = 4
_cache: Dict[Tuple[str, str, int], ImageTk.PhotoImage] = {}

TRANSPARENT = (0, 0, 0, 0)


def _draw_trash(draw: ImageDraw.ImageDraw, s: int, color: str) -> None:
    """Papelera: tapa con asa y cuerpo con tres ranuras."""
    u = s / 64
    draw.rounded_rectangle((25 * u, 4 * u, 39 * u, 12 * u), radius=3 * u, fill=color)
    draw.rounded_rectangle((10 * u, 10 * u, 54 * u, 17 * u), radius=3 * u, fill=color)
    draw.polygon([(15 * u, 21 * u), (49 * u, 21 * u), (45 * u, 60 * u), (19 * u, 60 * u)],
                 fill=color)
    for x in (25, 32, 39):
        draw.line((x * u, 28 * u, x * u, 53 * u), fill=TRANSPARENT, width=int(4 * u))


def _draw_copy(draw: ImageDraw.ImageDraw, s: int, color: str) -> None:
    """Dos hojas superpuestas: la de atrás en contorno y la de delante encima."""
    u = s / 64
    width = int(6 * u)
    draw.rounded_rectangle((22 * u, 4 * u, 58 * u, 44 * u), radius=6 * u,
                           outline=color, width=width)
    # Borra lo que queda bajo la hoja de delante para que no se vean las líneas de atrás
    draw.rounded_rectangle((3 * u, 17 * u, 45 * u, 61 * u), radius=8 * u, fill=TRANSPARENT)
    draw.rounded_rectangle((6 * u, 20 * u, 42 * u, 58 * u), radius=6 * u,
                           outline=color, width=width)


def _glyph_font(size: int) -> ImageFont.ImageFont:
    """Segoe UI en negrita (incluida en Windows); si no está, la fuente por defecto."""
    for name in ("segoeuib.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_badge(draw: ImageDraw.ImageDraw, s: int, color: str, glyph: str) -> None:
    """Círculo de color con un símbolo blanco: i, !, ?, ✓ o ×."""
    u = s / 64
    draw.ellipse((2 * u, 2 * u, 62 * u, 62 * u), fill=color)
    white = "#ffffff"
    if glyph == "check":
        draw.line([(18 * u, 33 * u), (28 * u, 43 * u), (46 * u, 22 * u)],
                  fill=white, width=int(7 * u), joint="curve")
    elif glyph == "cross":
        for a, b in (((21, 21), (43, 43)), ((43, 21), (21, 43))):
            draw.line([(a[0] * u, a[1] * u), (b[0] * u, b[1] * u)],
                      fill=white, width=int(7 * u))
    else:
        font = _glyph_font(int(40 * u))
        draw.text((32 * u, 33 * u), glyph, fill=white, font=font, anchor="mm")


_DRAWERS = {"trash": _draw_trash, "copy": _draw_copy}

# Insignias de los diálogos: tipo -> símbolo
BADGE_GLYPHS = {"info": "i", "warning": "!", "question": "?",
                "success": "check", "error": "cross"}


def get_badge(kind: str, color: str, size: int = 40) -> ImageTk.PhotoImage:
    """Insignia redonda para los diálogos (info, warning, question, success, error)."""
    key = (f"badge-{kind}", color, size)
    if key not in _cache:
        big = size * _SCALE
        image = Image.new("RGBA", (big, big), TRANSPARENT)
        _draw_badge(ImageDraw.Draw(image), big, color, BADGE_GLYPHS[kind])
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        _cache[key] = ImageTk.PhotoImage(image)
    return _cache[key]


def get_icon(name: str, color: str = "#ffffff", size: int = 16) -> ImageTk.PhotoImage:
    """
    Devuelve un icono como PhotoImage (cacheado, para que Tk no lo libere).

    Args:
        name: "trash" o "copy"
        color: Color del dibujo
        size: Lado en píxeles
    """
    key = (name, color, size)
    if key not in _cache:
        big = size * _SCALE
        image = Image.new("RGBA", (big, big), TRANSPARENT)
        _DRAWERS[name](ImageDraw.Draw(image), big, color)
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        _cache[key] = ImageTk.PhotoImage(image)
    return _cache[key]
