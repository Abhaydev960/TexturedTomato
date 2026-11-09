import cv2
import numpy as np


def _prepare(decal: np.ndarray, scale: float, angle: float) -> np.ndarray:
    """Scale + rotate a decal. Returns float32 PREMULTIPLIED RGBA in 0..1
    (premultiplied avoids dark fringes around transparent edges)."""
    f = decal.astype(np.float32) / 255.0
    f[..., :3] *= f[..., 3:4]
    h, w = f.shape[:2]
    if abs(scale - 1.0) > 1e-3:
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        f = cv2.resize(f, (nw, nh),
                       interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
        f = np.clip(f, 0, 1)
        h, w = nh, nw
    if abs(angle) > 1e-3:
        # negative: Qt rotates clockwise, OpenCV counter-clockwise
        m = cv2.getRotationMatrix2D((w / 2, h / 2), -angle, 1.0)
        c, s = abs(m[0, 0]), abs(m[0, 1])
        nw, nh = int(np.ceil(h * s + w * c)), int(np.ceil(h * c + w * s))
        m[0, 2] += nw / 2 - w / 2
        m[1, 2] += nh / 2 - h / 2
        f = cv2.warpAffine(f, m, (nw, nh), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return f


def _composite(dst: np.ndarray, src: np.ndarray, x0: int, y0: int) -> None:
    """Alpha-composite premultiplied `src` onto uint8 RGBA `dst` in place."""
    H, W = dst.shape[:2]
    h, w = src.shape[:2]
    bx0, by0, bx1, by1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if bx0 >= bx1 or by0 >= by1:
        return
    s = src[by0 - y0:by1 - y0, bx0 - x0:bx1 - x0]
    region = dst[by0:by1, bx0:bx1].astype(np.float32) / 255.0
    da = region[..., 3:4]
    d_pm = np.concatenate([region[..., :3] * da, da], axis=-1)
    out = s + d_pm * (1.0 - s[..., 3:4])
    oa = out[..., 3:4]
    rgb = np.divide(out[..., :3], oa, out=np.zeros_like(out[..., :3]), where=oa > 1e-6)
    res = np.concatenate([rgb, oa], axis=-1)
    dst[by0:by1, bx0:bx1] = (np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)


def stamp(base, decal, center, scale=1.0, angle=0.0, opacity=1.0, wrap=False):
    """Paint `decal` (RGBA) onto `base` (RGBA) centred at `center` (x, y px).
    Returns a new array. wrap=True makes it wrap around the edges (for tileable textures)."""
    src = _prepare(decal, scale, angle) * float(opacity)
    h, w = src.shape[:2]
    x0 = int(round(center[0] - w / 2))
    y0 = int(round(center[1] - h / 2))
    out = base.copy()
    H, W = base.shape[:2]
    offsets = [(dx, dy) for dx in (-W, 0, W) for dy in (-H, 0, H)] if wrap else [(0, 0)]
    for dx, dy in offsets:
        _composite(out, src, x0 + dx, y0 + dy)
    return out
