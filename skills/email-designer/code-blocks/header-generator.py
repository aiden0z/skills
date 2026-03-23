"""
Header Generator — Create Banner Images for Email Headers
===========================================================
Composites title and subtitle text onto a background image or solid color
to produce a professional header banner for email templates.

Usage by Agent:
    1. User provides background image, or choose solid color
    2. Call HeaderGenerator().generate(title, subtitle, output_path)
    3. Reference output in HTML: <img src="images/header_banner.jpg">

Dependencies: pillow (auto-installed by deps-checker.py)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# Display width reference (HTML img tag width)
DISPLAY_WIDTH = 1200

# Font sizes at 1x display scale (scaled by actual image width / DISPLAY_WIDTH)
TITLE_FONT_SIZE_1X = 36
SUBTITLE_FONT_SIZE_1X = 18
TITLE_SUBTITLE_GAP_1X = 20

# Output settings
JPEG_QUALITY = 90
DEFAULT_BANNER_HEIGHT = 200

# System font fallbacks (no bundled fonts — use what's available)
_SYSTEM_FONTS_BOLD = [
    ("/System/Library/Fonts/STHeiti Medium.ttc", 1),      # macOS
    ("C:/Windows/Fonts/msyhbd.ttc", 0),                    # Windows (YaHei Bold)
    ("C:/Windows/Fonts/simhei.ttf", 0),                    # Windows (SimHei)
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 0),  # Linux
]

_SYSTEM_FONTS_REGULAR = [
    ("/System/Library/Fonts/STHeiti Light.ttc", 1),        # macOS
    ("C:/Windows/Fonts/msyh.ttc", 0),                      # Windows (YaHei)
    ("C:/Windows/Fonts/simsun.ttc", 0),                    # Windows (SimSun)
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 0),  # Linux
]


def _load_font(system_fallbacks: list, size: int):
    """Load a font: try system fonts, fall back to Pillow default."""
    for path, index in system_fallbacks:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size, index=index)
            except Exception:
                continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple. Falls back to blue on invalid input."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (37, 99, 235)  # fallback: #2563eb
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return (37, 99, 235)


class HeaderGenerator:
    """Generate header banner images by compositing text onto backgrounds.

    Usage:
        gen = HeaderGenerator()

        # With background image
        path = gen.generate('Weekly Report', 'Week 12 | 2026-03-23',
                            'images/header_banner.jpg', bg_image='bg.png')

        # With solid color
        path = gen.generate('Newsletter', 'March 2026',
                            'images/header_banner.jpg', bg_color='#2563eb')
    """

    def generate(
        self,
        title: str,
        subtitle: str,
        output_path: str,
        bg_image: str = None,
        bg_color: str = "#2563eb",
        width: int = None,
    ) -> str:
        """Generate header banner image.

        Args:
            title: Main title text
            subtitle: Subtitle text (rendered at 85% opacity)
            output_path: Where to save the output JPEG
            bg_image: Path to background image (optional)
            bg_color: Hex color for solid background (default blue, used when no bg_image)
            width: Override width in pixels (default: DISPLAY_WIDTH or bg image width)

        Returns:
            Absolute path to generated image
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if bg_image and Path(bg_image).exists():
            bg = Image.open(bg_image).convert("RGBA")
            render_w, render_h = bg.size
        else:
            render_w = width or DISPLAY_WIDTH
            render_h = DEFAULT_BANNER_HEIGHT
            rgb = _hex_to_rgb(bg_color)
            bg = Image.new("RGBA", (render_w, render_h), (*rgb, 255))

        # Scale font sizes based on image width relative to display width
        scale = render_w / DISPLAY_WIDTH
        title_size = round(TITLE_FONT_SIZE_1X * scale)
        subtitle_size = round(SUBTITLE_FONT_SIZE_1X * scale)
        gap = round(TITLE_SUBTITLE_GAP_1X * scale)

        draw = ImageDraw.Draw(bg)

        # Load fonts
        title_font = _load_font(_SYSTEM_FONTS_BOLD, title_size)
        subtitle_font = _load_font(_SYSTEM_FONTS_REGULAR, subtitle_size)

        # Measure text
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]

        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_h = subtitle_bbox[3] - subtitle_bbox[1]

        # Center text block vertically
        total_text_height = title_h + gap + subtitle_h
        block_top = (render_h - total_text_height) // 2

        # Draw title (centered, white)
        draw.text(
            ((render_w - title_w) // 2, block_top),
            title,
            font=title_font,
            fill=(255, 255, 255, 255),
        )

        # Draw subtitle (centered, 85% opacity white)
        draw.text(
            ((render_w - subtitle_w) // 2, block_top + title_h + gap),
            subtitle,
            font=subtitle_font,
            fill=(255, 255, 255, 217),
        )

        # Convert RGBA → RGB (white background) and save as JPEG
        final = Image.new("RGB", bg.size, (255, 255, 255))
        final.paste(bg, mask=bg.split()[3])
        final.save(str(output_path), "JPEG", quality=JPEG_QUALITY, optimize=True)

        return str(output_path.resolve())
