import cv2
import numpy as np


def order_points(pts) -> np.ndarray:
    """Return the 4 points ordered TL, TR, BR, BL (so click order doesn't matter)."""
    pts = np.asarray(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    d = pts[:, 1] - pts[:, 0]
    return np.array([pts[s.argmin()], pts[d.argmin()],
                     pts[s.argmax()], pts[d.argmax()]], dtype=np.float32)


def extract_quad(img: np.ndarray, pts, out_size=None) -> np.ndarray:
    """Unwarp the quad `pts` of `img` into a flat rectangle.
    out_size: None = natural size, or (w, h) to resize the result."""
    src = order_points(pts)
    tl, tr, br, bl = src
    w = int(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    h = int(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
    if w < 2 or h < 2:
        raise ValueError("Selected area is too small")
    dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
    m = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(img, m, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    if out_size is not None and tuple(out_size) != (w, h):
        shrink = out_size[0] * out_size[1] < w * h
        out = cv2.resize(out, tuple(out_size),
                         interpolation=cv2.INTER_AREA if shrink else cv2.INTER_CUBIC)
    return out
