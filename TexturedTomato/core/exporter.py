import os

import cv2
import numpy as np


def export_image(path: str, rgba: np.ndarray) -> str:
    ext = os.path.splitext(path)[1].lower()
    if not ext:
        path += ".png"
        ext = ".png"
    if ext in (".jpg", ".jpeg"):  # no alpha in JPEG: flatten over white
        a = rgba[..., 3:4].astype(np.float32) / 255
        rgb = rgba[..., :3] * a + 255 * (1 - a)
        out = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
    else:
        out = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)
    ok, buf = cv2.imencode(ext, out)
    if not ok:
        raise ValueError(f"Could not encode as {ext}")
    buf.tofile(path)
    return path
