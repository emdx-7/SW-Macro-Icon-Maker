"""
Interactively crop an image to a square region and save it to inputs/.

- Opens a file picker to choose any image
- Displays the image with a draggable square crop selector
- Saves the crop to inputs/<filename>_crop.<ext>

Run:
    python crop.py
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow not installed. Run: pip install pillow")

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    sys.exit("tkinter not available — it ships with standard Python on Windows")

INPUTS = Path(__file__).parent / "inputs"
SUPPORTED = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.gif', '.webp', '.bmp'}


class CropSelector:
    def __init__(self, root, img: Image.Image, src_path: Path):
        self.root = root
        self.src_path = src_path
        self.orig = img

        # Fit image to max 800x800 for display
        display_size = 800
        scale = min(display_size / img.width, display_size / img.height, 1.0)
        self.scale = scale
        disp_w = int(img.width * scale)
        disp_h = int(img.height * scale)

        import PIL.ImageTk
        self.tk_img = PIL.ImageTk.PhotoImage(img.resize((disp_w, disp_h), Image.LANCZOS))

        root.title(f"Crop — {src_path.name}  |  drag to select square, Enter to save")

        self.canvas = tk.Canvas(root, width=disp_w, height=disp_h, cursor="crosshair")
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        tk.Label(root, text="Drag a square region, then press Enter to save  |  Esc to cancel").pack()

        self.rect = None
        self.start = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        root.bind("<Return>", self.on_save)
        root.bind("<Escape>", lambda e: root.destroy())

        self.crop_box = None  # in original image coords

    def on_press(self, e):
        self.start = (e.x, e.y)
        if self.rect:
            self.canvas.delete(self.rect)

    def on_drag(self, e):
        if not self.start:
            return
        x0, y0 = self.start
        # Force square: use the smaller side
        size = min(abs(e.x - x0), abs(e.y - y0))
        x1 = x0 + size * (1 if e.x >= x0 else -1)
        y1 = y0 + size * (1 if e.y >= y0 else -1)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)
        # Store in original coords
        s = self.scale
        self.crop_box = (
            int(min(x0, x1) / s),
            int(min(y0, y1) / s),
            int(max(x0, x1) / s),
            int(max(y0, y1) / s),
        )

    def on_release(self, e):
        self.on_drag(e)

    def on_save(self, e=None):
        if not self.crop_box:
            print("No region selected.")
            return
        INPUTS.mkdir(exist_ok=True)
        import shutil
        INPUTS.mkdir(exist_ok=True)
        stem = self.src_path.name.removeprefix("_uncropped_")
        uncropped_path = INPUTS / ("_uncropped_" + stem)
        out_path = INPUTS / stem
        shutil.copy2(str(self.src_path), str(uncropped_path))
        cropped = self.orig.crop(self.crop_box)
        cropped.save(str(out_path))
        print(f"  [saved] {out_path.name}  (original copied to {uncropped_path.name})")
        self.root.destroy()


def main():
    # Hidden root just for the file dialog
    root = tk.Tk()
    root.withdraw()

    path_str = filedialog.askopenfilename(
        title="Select an image to crop",
        initialdir=str(INPUTS) if INPUTS.exists() else str(Path(__file__).parent),
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.tiff *.tif *.gif *.webp *.bmp"),
                   ("All files", "*.*")]
    )
    if not path_str:
        print("No file selected.")
        return

    src = Path(path_str)
    if src.suffix.lower() not in SUPPORTED:
        sys.exit(f"Unsupported format: {src.suffix}")

    img = Image.open(src)

    root.deiconify()
    app = CropSelector(root, img, src)
    root.mainloop()


if __name__ == '__main__':
    main()
