"""Gera as imagens leves da página de revisão a partir dos quadros finais e da v1."""
import os
from PIL import Image
A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(A, 'web')
for n in range(1, 6):
    Image.open(os.path.join(A, 'quadros', f'quadro{n}.png')).convert('RGB').resize((720, 1280), Image.LANCZOS).save(os.path.join(W, f'q{n}_v2.jpg'), quality=86, optimize=True)
    Image.open(os.path.join(A, 'v1', f'v1_quadro{n}.jpg')).convert('RGB').resize((540, 960), Image.LANCZOS).save(os.path.join(W, f'q{n}_v1.jpg'), quality=82, optimize=True)
Image.open(os.path.join(A, 'quadros', 'quadro6_assinatura.png')).convert('RGB').resize((540, 960), Image.LANCZOS).save(os.path.join(W, 'assinatura.jpg'), quality=86, optimize=True)
print('ok')
