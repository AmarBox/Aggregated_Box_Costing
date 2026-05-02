"""One-shot script to (re)generate backend/app_icon.ico.

The icon is committed to the repo; rerun this only if the design needs
to change. The .ico is referenced by build.ps1 (PyInstaller --icon) and
loaded at runtime by launcher.py for the system tray.
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).parent / "app_icon.ico"
SIZE = 256
LINE_COLOR = (101, 67, 33, 255)  # cardboard brown
BG_COLOR = (0, 0, 0, 0)          # transparent
LINE_WIDTH = 10


def draw_box(img: Image.Image) -> None:
    d = ImageDraw.Draw(img)

    margin = 16
    depth = 36
    x0 = margin
    y1 = SIZE - margin
    x1 = SIZE - margin - depth
    y0 = margin + depth
    xd = x1 + depth
    yd = y0 - depth

    d.rectangle([x0, y0, x1, y1], outline=LINE_COLOR, width=LINE_WIDTH)
    d.line([x0, y0, x0 + depth, yd], fill=LINE_COLOR, width=LINE_WIDTH)
    d.line([x1, y0, xd, yd], fill=LINE_COLOR, width=LINE_WIDTH)
    d.line([x0 + depth, yd, xd, yd], fill=LINE_COLOR, width=LINE_WIDTH)
    d.line([x1, y1, xd, y1 - depth], fill=LINE_COLOR, width=LINE_WIDTH)
    d.line([xd, yd, xd, y1 - depth], fill=LINE_COLOR, width=LINE_WIDTH)


def main() -> None:
    img = Image.new("RGBA", (SIZE, SIZE), BG_COLOR)
    draw_box(img)
    img.save(
        OUT,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
