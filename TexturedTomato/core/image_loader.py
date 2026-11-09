"""Everything in the app is RGBA uint8 numpy arrays (H, W, 4)."""
import cv2
import numpy as np


def to_rgba(img: np.ndarray) -> np.ndarray:
    if img.dtype == np.uint16:
        img = (img >> 8).astype(np.uint8)
    elif img.dtype != np.uint8:
        img = np.clip(img * 255, 0, 255).astype(np.uint8)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
    if img.shape[2] == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)


def load_image(path: str) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)  # works with unicode paths on Windows
    img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    return to_rgba(img)
