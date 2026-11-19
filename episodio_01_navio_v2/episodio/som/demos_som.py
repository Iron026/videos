"""Demonstrações comparativas do sound design: os mesmos 4 trechos com o som ANTERIOR (sintético) e com GRAVAÇÕES
REAIS — mesma imagem, mesma narração; cada trecho igualado em loudness integrado (−16 LUFS) para uma comparação justa."""
import os, subprocess, re, json
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); T = os.path.join(EP, 'montagem_demos'); os.makedirs(T, exist_ok=True)
TR = [('Abertura', 0.0, 15.1), ('Estaleiro e solda', 15.1, 30.3), ('Empuxo, retomada e experimento', 48.0, 95.0), ('Avaria e inundação', 134.0, 155.0)]
VERS = [('sintetico', 'Som anterior (sintético)', os.path.join(A, 'bib', 'audio_ep01_sintetico.wav')), ('real', 'Gravações reais', os.path.join(EP, 'audio_ep01_real.wav'))]
F = ImageFont.truetype(os.path.join(EP, '..', 'fontes', 'Montserrat-800.ttf'), 22)
def lufs(p):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = e[e.rfind('Summary:'):]; return float(re.search(r'I:\s+(-?[\d.]+)', s).group(1)), float(re.search(r'Peak:\s+(-?[\d.]+)', s).group(1))
medidas = {}; partes = {v: [] for v, _, _ in VERS}; ab = []
for k, (nome, a, b) in enumerate(TR):
    for v, rotulo, au in VERS:
        bruto = os.path.join(T, f'{v}_{k}_bruto.mp4')
        subprocess.run(['python3', os.path.join(EP, 'montar_ep01.py'), 'revisao', bruto, str(a), str(b)], env=dict(os.environ, AUDIO_EP01=au), check=True, capture_output=True)
        i, _ = lufs(bruto); g = -16.0 - i
        im = Image.new('RGBA', (540, 44), (32, 43, 87, 235) if v == 'sintetico' else (243, 181, 68, 235)); d = ImageDraw.Draw(im)
        d.text((14, 10), f'{rotulo} · {nome}', font=F, fill=(246, 244, 236) if v == 'sintetico' else (32, 43, 87)); tag = os.path.join(T, f'tag_{v}_{k}.png'); im.save(tag)
        out = os.path.join(T, f'{v}_{k}.mp4')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', bruto, '-i', tag, '-filter_complex', '[0:v][1:v]overlay=0:0,format=yuv420p[v]', '-map', '[v]', '-map', '0:a',
                        '-af', f'volume={g:.2f}dB,alimiter=limit=-1.5dB:level=disabled', '-c:v', 'libx264', '-crf', '19', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out], check=True)
        i2, p2 = lufs(out); medidas[f'{v}_{k}'] = dict(trecho=nome, lufs=i2, pico_dbtp=p2, ganho_db=round(g, 2))
        partes[v].append(out); ab.append(out)
for nome, lista in (('ep01_demo_som_sintetico.mp4', partes['sintetico']), ('ep01_demo_som_real.mp4', partes['real']), ('ep01_demo_som_AB.mp4', ab)):
    txt = os.path.join(T, 'l.txt'); open(txt, 'w').write(''.join(f"file '{p}'\n" for p in lista))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', txt, '-c', 'copy', '-movflags', '+faststart', os.path.join(EP, nome)], check=True)
json.dump(medidas, open(os.path.join(A, 'demos_medidas.json'), 'w'), ensure_ascii=False, indent=1); print(json.dumps(medidas, ensure_ascii=False, indent=1))
