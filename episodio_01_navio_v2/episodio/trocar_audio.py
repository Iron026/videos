"""Troca o áudio do Ep. 01 SEM refazer animação 3D nem precisar dos quadros renderizados: usa o master de imagem sem
legendas (ep01_master_imagem_sem_legendas.mp4), queima as legendas da narração escolhida (mesmo estilo da montagem) e
coloca a nova mixagem com o mesmo controle de loudness/pico (−14 LUFS, pico verdadeiro ≤ −1,6 dBTP no AAC).

Uso:  [NARRACAO_EP01_DIR=<pasta com palavras.json>] python3 episodio/trocar_audio.py <mixagem.wav> <saida.mp4> [master.mp4]
Ex.:  NARRACAO_EP01_DIR=voz/narracao_nova_encaixada python3 episodio/trocar_audio.py episodio/audio_ep01_hibrido_vozpaga.wav saida.mp4
Para o render definitivo em 1080 × 1920 os quadros são renderizados de novo (perfil 'final' de montar_ep01.py), e o áudio
entra da mesma forma (AUDIO_EP01 + NARRACAO_EP01_DIR): a imagem não depende do áudio."""
import os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw
A = os.path.dirname(os.path.abspath(__file__))
mix, saida = sys.argv[1], sys.argv[2]; master = sys.argv[3] if len(sys.argv) > 3 else os.path.join(A, 'ep01_master_imagem_sem_legendas.mp4')
sys.argv = ['montar_ep01.py', 'revisao', saida]; sys.path.insert(0, A)
import montar_ep01 as M                                  # mesmas fontes, cores, regras de legenda e controle de loudness

W, H = M.W, M.H; n = int(round(M.DUR * M.FPS)); af = M.loudness(mix)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', master, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(M.FPS), '-i', '-', '-i', mix, '-af', af,
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest',
                        '-movflags', '+faststart', '-metadata', 'title=De Olho no Invisível · Ep. 01 · versão de revisão (não publicar)', saida], stdin=subprocess.PIPE)
for i in range(n):
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    img = Image.frombytes('RGB', (W, H), raw); g = i / M.FPS; d = ImageDraw.Draw(img)
    for (a, b, txt) in M.LEG:
        if a <= g < b:
            d.text((W // 2, int(0.70 * H)), txt, font=M.F_LEG, fill=(255, 255, 255), stroke_width=max(2, int(7 * M.ESC)), stroke_fill=M.ESCURO, anchor='mm')
    enc.stdin.write(img.tobytes())
enc.stdin.close(); enc.wait(); dec.wait(); print('ok', saida, i + 1, 'quadros')
