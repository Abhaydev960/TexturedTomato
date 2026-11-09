import cv2
import numpy as np


def _blend_axis(f: np.ndarray, axis: int, width: float) -> np.ndarray:
    """Cross-fade the image with a copy rolled by half along one axis.
    Mask is 0 at the borders (rolled copy, whose borders are neighbours in the
    original => wraps perfectly) and 1 at the centre (hides the rolled copy's seam)."""
    n = f.shape[axis]
    d = 1.0 - np.abs(np.linspace(-1.0, 1.0, n, dtype=np.float32))  # 0 edge .. 1 centre
    t = np.clip(d / max(width, 1e-3), 0.0, 1.0)
    m = t * t * (3 - 2 * t)  # smoothstep
    shape = [1] * f.ndim
    shape[axis] = n
    m = m.reshape(shape)
    return f * m + np.roll(f, n // 2, axis=axis) * (1 - m)


def make_seamless(img: np.ndarray, width: float = 0.5) -> np.ndarray:
    """width (0..1): how far from the edges the blend reaches. Small = less
    ghosting but a harder transition; 1.0 = blend across the whole image."""
    f = img.astype(np.float32)
    f = _blend_axis(f, 1, width)  # horizontal pass
    f = _blend_axis(f, 0, width)  # vertical pass (keeps horizontal tiling intact)
    return np.clip(f + 0.5, 0, 255).astype(np.uint8)


def tile_preview(img: np.ndarray, n: int = 3, max_tile: int = 1024) -> np.ndarray:
    """n x n tiled preview. Tiles are downscaled first so huge textures stay light."""
    h, w = img.shape[:2]
    s = max_tile / max(h, w)
    if s < 1:
        img = cv2.resize(img, (max(1, int(w * s)), max(1, int(h * s))),
                         interpolation=cv2.INTER_AREA)
    return np.tile(img, (n, n, 1))
