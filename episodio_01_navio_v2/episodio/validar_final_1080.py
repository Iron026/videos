"""Validação do arquivo DEFINITIVO (1080 × 1920) contra a revisão aprovada (ep01_revisao_s08b_corrigido.mp4, 540 × 960).
Uso: python3 episodio/validar_final_1080.py <final.mp4> [aprovado.mp4]   → validacao_final_1080.json
Imagem: formato, 5.040 quadros, quadros pretos/congelados, erros de decodificação; semelhança quadro a quadro (final reduzido a
540 × 960 × aprovado, SEM a região do selo de revisão, que só o aprovado tem); continuidade temporal (diferença entre quadros
consecutivos no final × no aprovado: cortes e fusões nos mesmos instantes; "piscadas" locais novas); janelas 146,5–148,3 s;
ausência do selo. Áudio: mesmo áudio do aprovado (desvio e resíduo), sincronia da narração, loudness e pico verdadeiro no AAC."""
import os, sys, re, json, subprocess, numpy as np, soundfile as sf
from scipy.ndimage import uniform_filter
A = os.path.dirname(os.path.abspath(__file__)); SR = 48000
final = sys.argv[1]; aprov = sys.argv[2] if len(sys.argv) > 2 else os.path.join(A, 'ep01_revisao_s08b_corrigido.mp4')
ff = lambda *a: subprocess.run(['ffmpeg', '-hide_banner', *a], capture_output=True, text=True).stderr
probe = lambda f, e, s='v:0': subprocess.run(['ffprobe', '-v', 'error', '-select_streams', s, '-show_entries', e, '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip()
R = {}
R['formato'] = dict(video=probe(final, 'stream=codec_name,width,height,r_frame_rate,pix_fmt'), audio=probe(final, 'stream=codec_name,sample_rate,channels', 'a:0'),
                    duracao_video_s=float(probe(final, 'stream=duration')), duracao_audio_s=float(probe(final, 'stream=duration', 'a:0')),
                    quadros=int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', final], capture_output=True, text=True).stdout.strip()),
                    titulo=subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags=title', '-of', 'csv=p=0', final], capture_output=True, text=True).stdout.strip(),
                    tamanho_mb=round(os.path.getsize(final) / 1e6, 1))
e = ff('-i', final, '-vf', 'blackdetect=d=0.1:pix_th=0.05,freezedetect=n=0.001:d=1.0', '-an', '-f', 'null', '-')
R['integridade'] = dict(trechos_pretos=e.count('black_start'), congelamentos=e.count('freeze_start'), erros_decodificacao=len([l for l in ff('-v', 'error', '-i', final, '-f', 'null', '-').splitlines() if l.strip()]))
# ---- quadro a quadro (cinza, 540 × 960)
def ler(f, scale):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale=540:960:flags={scale}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(540 * 960)
        if len(b) < 540 * 960: break
        yield np.frombuffer(b, np.uint8).astype(np.float32).reshape(960, 540)
def ssim_mapa(a, b):
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2; ma, mb = uniform_filter(a, 7), uniform_filter(b, 7)
    va, vb, cab = uniform_filter(a * a, 7) - ma ** 2, uniform_filter(b * b, 7) - mb ** 2, uniform_filter(a * b, 7) - ma * mb
    return ((2 * ma * mb + c1) * (2 * cab + c2)) / ((ma ** 2 + mb ** 2 + c1) * (va + vb + c2))
SELO = (slice(25, 70), slice(5, 290))                 # região do selo de revisão em 540 × 960 (com folga)
masc = np.ones((960, 540), bool); masc[SELO] = False
ss, dF, dA, pisc, selo_dif, jan_f, jan_a, prevF, prevA, pF2, pA2 = [], [], [], [], [], [], [], None, None, None, None
for i, (f, a) in enumerate(zip(ler(final, 'area'), ler(aprov, 'bilinear'))):
    ss.append(float(ssim_mapa(f, a)[masc].mean())); selo_dif.append(float(np.abs(f[SELO] - a[SELO]).mean()))
    if prevF is not None:
        dF.append(float(np.abs(f - prevF).mean())); dA.append(float(np.abs(a - prevA).mean()))
        if pF2 is not None:   # cintilação local: 2ª diferença em blocos de 20 px, final × aprovado
            lf = np.abs(f - 2 * prevF + pF2)[:960, :540].reshape(48, 20, 27, 20).mean((1, 3)); la = np.abs(a - 2 * prevA + pA2).reshape(48, 20, 27, 20).mean((1, 3))
            if (lf > la * 1.5 + 6).any(): pisc.append(round((i - 1) / 30, 3))
            if 146.5 <= i / 30 <= 148.3: jan_f.append(float(lf[:16, :14].mean())); jan_a.append(float(la[:16, :14].mean()))
    pF2, pA2, prevF, prevA = prevF, prevA, f, a
ss = np.array(ss); t = np.arange(len(ss)) / 30
SEGS = [('s01', 0, 4.4), ('s02', 4.4, 15.1), ('s03', 15.1, 30.3), ('s04', 30.3, 41.55), ('s05', 41.55, 48.0), ('s0607', 48.0, 74.85), ('s08a', 74.85, 83.85), ('s08b', 83.85, 94.55),
        ('s09', 94.55, 117.2), ('s10', 117.2, 123.65), ('s11', 123.65, 134.0), ('s12x', 134.0, 137.0), ('s12', 137.0, 154.6), ('s13', 154.6, 168.0)]
dF, dA = np.array(dF), np.array(dA)
cortesF = set(np.where(dF > np.median(dF) * 6 + 3)[0]); cortesA = set(np.where(dA > np.median(dA) * 6 + 3)[0])
R['semelhanca_ao_aprovado'] = dict(quadros_comparados=len(ss), ssim_medio=round(float(ss.mean()), 4), ssim_min=round(float(ss.min()), 4), ssim_min_t=round(float(t[ss.argmin()]), 2),
    quadros_abaixo_0_93=[round(float(x), 2) for x in t[ss < 0.93]][:40], por_segmento={n: dict(ssim_medio=round(float(ss[(t >= a) & (t < b)].mean()), 4), ssim_min=round(float(ss[(t >= a) & (t < b)].min()), 4)) for n, a, b in SEGS})
R['continuidade'] = dict(correlacao_dif_entre_quadros=round(float(np.corrcoef(dF, dA)[0, 1]), 4), saltos_so_no_final=[round((i + 1) / 30, 2) for i in sorted(cortesF - cortesA)],
    saltos_so_no_aprovado=[round((i + 1) / 30, 2) for i in sorted(cortesA - cortesF)], piscadas_locais_novas=pisc[:40], n_piscadas_locais_novas=len(pisc))
R['janelas_146_5_148_3'] = dict(cintilacao_final=round(float(np.mean(jan_f)), 2) if jan_f else None, cintilacao_aprovado=round(float(np.mean(jan_a)), 2) if jan_a else None)
sd = np.array(selo_dif); R['selo_revisao'] = dict(dif_media_regiao_do_selo=round(float(sd.mean()), 1), quadros_com_regiao_igual_ao_aprovado=int((sd < 4).sum()), nota='o aprovado tem o selo; diferença alta em todos os quadros = selo ausente no final')
# ---- áudio
def aud(f):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2)
af, aa = aud(final), aud(aprov); n = min(len(af), len(aa)); m = af[:n].mean(1); ma_ = aa[:n].mean(1)
k = 4800; c = np.correlate(m[SR * 10:SR * 20], ma_[SR * 10 - k:SR * 20 + k], 'valid'); desl = (int(np.argmax(c)) - k) / SR
res = 20 * np.log10(np.sqrt(np.mean((m - ma_) ** 2)) / np.sqrt(np.mean(ma_ ** 2)) + 1e-12)
voz = sf.read(os.path.join(A, 'stems', 'ep01_narracao_refinado_buzina.wav'))[0].mean(1)
def atraso(x, y, maxd=0.1):
    F = np.fft.rfft(x, 2 * len(x)) * np.conj(np.fft.rfft(y, 2 * len(x))); cc = np.fft.irfft(F); kk = int(maxd * SR); cc = np.concatenate([cc[-kk:], cc[:kk + 1]]); return (int(np.argmax(cc)) - kk) / SR
des = [round(atraso(m[int(s * SR):int((s + 4) * SR)], voz[int(s * SR):int((s + 4) * SR)]) * 1000, 1) for s in np.arange(2.0, 164.0, 8.0) if np.sqrt(np.mean(voz[int(s * SR):int((s + 4) * SR)] ** 2)) > 1e-3]
eb = ff('-i', final, '-af', 'ebur128=peak=true', '-f', 'null', '-'); eb = eb[eb.rfind('Summary:'):]
R['audio'] = dict(deslocamento_vs_aprovado_ms=round(desl * 1000, 2), residuo_vs_aprovado_db=round(float(res), 1), nivel_final_db=round(float(20 * np.log10(np.sqrt(np.mean(m ** 2)))), 2),
                  nivel_aprovado_db=round(float(20 * np.log10(np.sqrt(np.mean(ma_ ** 2)))), 2), sincronia_narracao_ms=dict(min=min(des), max=max(des), janelas=len(des)),
                  loudness_lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS', eb).group(1)), pico_verdadeiro_dbtp=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', eb).group(1)),
                  amostras_saturadas=int((np.abs(af) >= 0.999).sum()))
json.dump(R, open(os.path.join(A, 'validacao_final_1080.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
