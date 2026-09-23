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
