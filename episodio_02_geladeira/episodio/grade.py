"""Correção de cor sutil e uniforme do Ep. 01 (aplicada só à imagem 3D, antes dos rótulos e legendas):
curva em S leve (contraste), saturação +5 %, sombras levemente frias e altas luzes levemente quentes, e vinheta suave
(−10 % nas bordas). Unifica os planos sem mudar o caráter da imagem."""
import numpy as np
from PIL import Image
_V = {}


def _vinheta(w, h):
    if (w, h) not in _V:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32); r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / 1.414
        _V[(w, h)] = (1.0 - 0.10 * np.clip((r - 0.45) / 0.55, 0, 1) ** 1.6)[..., None]
    return _V[(w, h)]


def graduar(img, forca=1.0):
    a = np.asarray(img, dtype=np.float32) / 255.0
    s = a + forca * 0.06 * np.sin((a - 0.5) * np.pi) * 0.5 * (1 - np.abs(2 * a - 1)) * 2       # curva em S leve
    lum = (0.2126 * s[..., 0] + 0.7152 * s[..., 1] + 0.0722 * s[..., 2])[..., None]
    s = lum + (s - lum) * (1 + 0.05 * forca)                                                        # saturação +5 %
    tom = np.where(lum < 0.5, np.array([-0.012, 0.0, 0.016]), np.array([0.014, 0.006, -0.012])) * (np.abs(lum - 0.5) * 2) * forca
    s = (s + tom) * _vinheta(a.shape[1], a.shape[0]) ** forca
    return Image.fromarray((np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8))
