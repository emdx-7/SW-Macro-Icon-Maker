# BMP Convert — SolidWorks Macro Icon Converter

Converts images to BMP files usable as **SolidWorks macro toolbar icons**.

Output format: 8-bit 256-color, white background bitmap file

## Setup

```
pip install pillow
```

## Usage

1. Drop your images into the `inputs/` folder
2. Run `python convert.py`
3. Grab the `.bmp` files from `outputs/`
4. In SolidWorks: Tools > Customize > Commands tab > select your macro button > click the icon to assign the BMP

Already-converted files are skipped automatically.

## Supported input formats

PNG, JPG, JPEG, TIFF, TIF, GIF, WEBP, BMP

## Notes

- Detailed pictures get cooked since SW only supports small bitmap
- White areas become transparent (so grey/white) in the SolidWorks top bar
