"""
Convert images in the 'inputs' folder to SolidWorks macro icon BMPs in 'outputs'.

- Output is 20x20 pixels, 8-bit (256-color), white background = transparent on toolbar
- Skips files already converted (output already exists)
- Supported input formats: PNG, JPG, JPEG, TIFF, TIF, GIF, WEBP, BMP

Run:
    python convert.py
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("Pillow not installed. Run: pip install pillow")


INPUTS  = Path(__file__).parent / "inputs"
OUTPUTS = Path(__file__).parent / "outputs"
SUPPORTED = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.gif', '.webp', '.bmp'}
ICON_SIZE = (40, 40)


def to_solidworks_bmp(src: Path, dst: Path):
    img = Image.open(src)

    # Flatten alpha onto white background (white = transparent in SW toolbar)
    if img.mode in ('RGBA', 'LA', 'PA'):
        if img.mode == 'PA':
            img = img.convert('RGBA')
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Sharpen before scaling so edges survive the downsample
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

    # Scale to 20x20 using high-quality downsampling
    img = img.resize(ICON_SIZE, Image.LANCZOS)

    # Convert to 8-bit 256-color palette (required by SolidWorks macro icons)
    img = img.quantize(colors=256)

    img.save(str(dst), format='BMP')


def main():
    OUTPUTS.mkdir(exist_ok=True)

    candidates = [f for f in INPUTS.iterdir() if f.suffix.lower() in SUPPORTED]
    if not candidates:
        print("No supported images found in inputs/")
        return

    converted, skipped = 0, 0
    for src in sorted(candidates):
        dst = OUTPUTS / (src.stem + ".bmp")
        if dst.exists():
            print(f"  [skip] {src.name}  (already converted)")
            skipped += 1
            continue
        try:
            to_solidworks_bmp(src, dst)
            print(f"  [ok]   {src.name}  ->  outputs/{dst.name}")
            converted += 1
        except Exception as e:
            print(f"  [fail] {src.name}: {e}")

    print(f"\nDone. {converted} converted, {skipped} skipped.")


if __name__ == '__main__':
    main()
