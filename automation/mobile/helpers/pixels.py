"""Pixel oracle: is anything actually drawn inside an element's bounds?

For elements the accessibility tree misreports. Recon 3d: the OTP ``Incorrect code.`` text is
in the tree and reported ``visible=true`` while nothing is drawn — so neither presence nor
Appium visibility can decide "the error is shown", and a test built on them passes falsely.
The screenshot can: inside the element's box, text means pixels unlike the background.

Deliberately simple and objective: background = the most frequent colour in the box; "ink"
= pixels farther than ``threshold`` from it (sum of RGB differences). No image baselines.
"""

import io

from PIL import Image

INK_THRESHOLD = 60  # RGB distance that separates glyph pixels from a flat background
MIN_INK_RATIO = 0.03  # share of the box a drawn line of text covers at the very least


def ink_ratio(png: bytes, box: dict, scale: float, threshold: int = INK_THRESHOLD) -> float:
    """Share of pixels in ``box`` (points; x, y, width, height) that differ from its background.

    ``scale`` = screenshot pixels per point (iPhone 17: 1206 px / 402 pt = 3).
    """
    image = Image.open(io.BytesIO(png)).convert("RGB")
    left, top = round(box["x"] * scale), round(box["y"] * scale)
    right = round((box["x"] + box["width"]) * scale)
    bottom = round((box["y"] + box["height"]) * scale)
    region = image.crop((left, top, right, bottom))
    area = region.width * region.height
    if area == 0:
        return 0.0
    colours = region.getcolors(maxcolors=area)
    _, background = max(colours)
    ink = sum(
        count
        for count, colour in colours
        if sum(abs(a - b) for a, b in zip(colour, background, strict=True)) > threshold
    )
    return ink / area


# --- whole-screen oracles (module 01 Splash: no labelled element to ask the tree about) ---

SPLASH_DOWNSCALE = 6  # every 6th pixel is plenty for a flat brand colour and a 100-pt logo
COLOUR_TOLERANCE = 45  # summed RGB distance still counted as "the same colour"
LIGHT = 600  # R+G+B above this = the white logo on the brand colour


def hex_to_rgb(hex_colour: str) -> tuple[int, int, int]:
    """``"#782A2A"`` → (120, 42, 42). Raises ValueError on anything else (e.g. a prove-red text)."""
    value = hex_colour.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"not a #RRGGBB colour: {hex_colour!r}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _small(png: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(png)).convert("RGB")
    return image.resize(
        (image.width // SPLASH_DOWNSCALE, image.height // SPLASH_DOWNSCALE), Image.NEAREST
    )


def colour_share(png: bytes, rgb: tuple[int, int, int], tolerance: int = COLOUR_TOLERANCE) -> float:
    """Share of the whole screenshot painted in ``rgb`` (± ``tolerance``)."""
    small = _small(png)
    colours = small.getcolors(maxcolors=small.width * small.height) or []
    same = sum(
        count
        for count, colour in colours
        if sum(abs(a - b) for a, b in zip(colour, rgb, strict=True)) <= tolerance
    )
    return same / (small.width * small.height)


def light_blob_offset(
    png: bytes, points_wide: float, skip_top_pt: float = 60, skip_bottom_pt: float = 30
) -> tuple[float, float] | None:
    """Centre of the light pixels (the logo) relative to the screen centre, as fractions of the
    screen width / height; ``None`` when nothing light is drawn yet. The status bar (top) and the
    home indicator (bottom) are left out — their glyphs are light too."""
    small = _small(png)
    pt_per_px = points_wide / small.width
    top, bottom = int(skip_top_pt / pt_per_px), small.height - int(skip_bottom_pt / pt_per_px)
    xs: list[int] = []
    ys: list[int] = []
    pixels = small.load()
    for y in range(top, bottom):
        for x in range(small.width):
            if sum(pixels[x, y]) > LIGHT:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return (cx - small.width / 2) / small.width, (cy - small.height / 2) / small.height
