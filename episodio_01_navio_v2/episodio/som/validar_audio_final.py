"""Validação técnica da revisão final de áudio do Ep. 01 (itens 1–12 do pedido de finalização).
Medidas objetivas NÃO provam qualidade auditiva: servem para achar erros (dessincronia, clipping, corte brusco, excesso).
Uso: python3 som/validar_audio_final.py <final.mp4> <revisao_visual.mp4> [sufixo_com=refinado_buzina] [sufixo_sem=refinado]
Saída: som/validacao_audio_final.json"""
import os, sys, re, json, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from som_ep01 import lufs, pico_verdadeiro, db
from sintese import hpz, lpz
A = os.path.dirname(os.path.abspath(__file__)); EP = os.path.join(A, '..'); E = os.path.join(EP, 'stems'); SR = 48000
final, visual = sys.argv[1], sys.argv[2]; SC = sys.argv[3] if len(sys.argv) > 3 else 'refinado_buzina'; SS = sys.argv[4] if len(sys.argv) > 4 else 'refinado'
R = {}
def ff(*a): return subprocess.run(['ffmpeg', '-hide_banner', *a], capture_output=True, text=True).stderr
def probe(f, q): return subprocess.run(['ffprobe', '-v', 'error', *q, '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip()

# 1 · duração
R['1_duracao'] = dict(video_s=float(probe(final, ['-select_streams', 'v:0', '-show_entries', 'stream=duration'])),
                      audio_s=float(probe(final, ['-select_streams', 'a:0', '-show_entries', 'stream=duration'])),
                      quadros=int(probe(final, ['-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets'])),
                      resolucao=probe(final, ['-select_streams', 'v:0', '-show_entries', 'stream=width,height']))
# 2 · integridade da imagem: final × revisão visual aprovada (mesmo master + mesmas legendas; só a recodificação difere)
e = ff('-i', final, '-i', visual, '-lavfi', '[0:v][1:v]psnr', '-f', 'null', '-')
m = re.search(r'average:([\d.inf]+) min:([\d.inf]+)', e)
e2 = ff('-i', final, '-vf', 'blackdetect=d=0.1:pix_th=0.05,freezedetect=n=0.001:d=1.5', '-an', '-f', 'null', '-')
dec_err = ff('-v', 'error', '-i', final, '-f', 'null', '-').strip()
R['2_imagem'] = dict(psnr_medio_db=m.group(1), psnr_min_db=m.group(2), quadros_pretos=e2.count('black_start'), trechos_parados=e2.count('freeze_start'),
                     erros_de_decodificacao=len([l for l in dec_err.splitlines() if l.strip() and 'Error' in l]))
# áudio decodificado do AAC final
wav = os.path.join(A, '_val_final.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', wav], check=True)
fx = sf.read(wav)[0]; os.remove(wav)
voz = sf.read(f'{E}/ep01_narracao_{SC}.wav')[0]; mixw = sf.read(f'{EP}/audio_ep01_{SC}.wav')[0]; mixa = sf.read(f'{EP}/audio_ep01_{SS}.wav')[0]
# 3 · sincronia da narração: correlação cruzada do stem da voz com o áudio final em janelas de 4 s ao longo do episódio
def atraso(a, b, maxd=0.1):
    n = len(a); F = np.fft.rfft(a, 2 * n) * np.conj(np.fft.rfft(b, 2 * n)); c = np.fft.irfft(F)
    k = int(maxd * SR); c = np.concatenate([c[-k:], c[:k + 1]]); return (int(np.argmax(c)) - k) / SR
des = []
for t in np.arange(2.0, 164.0, 8.0):
    s = slice(int(t * SR), int((t + 4) * SR)); v = voz[s].mean(1)
    if np.sqrt(np.mean(v ** 2)) > 1e-3: des.append(round(atraso(fx[s].mean(1), v) * 1000, 1))
R['3_sincronia_narracao'] = dict(janelas=len(des), desvio_ms_min=min(des), desvio_ms_max=max(des), desvio_ms_mediana=float(np.median(des)))
# 4 · impactos (ataques medidos × eventos da animação) e buzinas
subprocess.run([sys.executable, os.path.join(A, 'sincronia_hibrido.py'), SC], check=True, capture_output=True)
sh = json.load(open(os.path.join(A, 'sincronia_hibrido.json')))
bz = sf.read(f'{E}/categorias/ep01_efeitos_buzina_{SC}.wav')[0].mean(1); w = int(0.01 * SR)
env = 20 * np.log10(np.sqrt(np.convolve(bz ** 2, np.ones(w) / w, 'same')) + 1e-9)
def janela_buzina(a, b):
    s = env[int(a * SR):int(b * SR)]; pk = s.max(); acima = np.where(s > pk - 20)[0]; aud = np.where(s > pk - 40)[0]
    return dict(inicio_audivel_s=round(a + aud[0] / SR, 2), ataque_pleno_s=round(a + acima[0] / SR, 2), pico_s=round(a + int(np.argmax(s)) / SR, 2),
                fim_audivel_s=round(a + aud[-1] / SR, 2))
R['4_sincronia'] = dict(impactos={k: v['desvio_ms'] for k, v in sh.items()}, maior_desvio_ms=max(abs(v['desvio_ms']) for v in sh.values()),
                        buzina_abertura=janela_buzina(5.0, 12.0), buzina_conclusao=janela_buzina(165.5, 168.0),
                        fim_da_ultima_palavra_s=166.12)
# 5 · clipping / distorção
R['5_clipping'] = dict(wav_pico_amostra_dbfs=round(float(20 * np.log10(np.abs(mixw).max())), 2), wav_amostras_acima_0_999=int((np.abs(mixw) >= 0.999).sum()),
                       aac_pico_amostra_dbfs=round(float(20 * np.log10(np.abs(fx).max())), 2), aac_amostras_acima_0_999=int((np.abs(fx) >= 0.999).sum()))
# 6 e 7 · loudness integrado e pico verdadeiro medidos no AAC final (ebur128 do ffmpeg)
e = ff('-i', final, '-af', 'ebur128=peak=true', '-f', 'null', '-'); e = e[e.rfind('Summary:'):]
R['6_loudness'] = dict(integrado_lufs=float(re.search(r'I:\s+(-?[\d.]+) LUFS', e).group(1)), lra_lu=float(re.search(r'LRA:\s+(-?[\d.]+) LU', e).group(1)))
R['7_pico_verdadeiro'] = dict(aac_dbtp=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', e).group(1)), meta='≤ −1,5 dBTP')
# 8 · clareza da voz: celular simulado (mono, 350 Hz–7 kHz), voz × resto em blocos de 100 ms com fala
def cel(x): return hpz(lpz(x.mean(1), 7000, 4), 350, 4)
cv = cel(voz); cr = cel(mixw) - cv; j = int(0.1 * SR); thr = np.mean(cv ** 2) * 0.05; snr = []
for i in range(0, len(cv) - j, j):
    pv = np.mean(cv[i:i + j] ** 2)
    if pv > thr: snr.append(10 * np.log10(pv / (np.mean(cr[i:i + j] ** 2) + 1e-12)))
snr = np.array(snr)
R['8_clareza_voz'] = dict(blocos_com_fala=len(snr), voz_10db_acima_pct=round(100 * float((snr >= 10).mean()), 1), snr_mediana_db=round(float(np.median(snr)), 1),
                          pior_bloco_db=round(float(snr.min()), 1))
# 9 · água (auditoria por seção)
subprocess.run([sys.executable, os.path.join(A, 'auditoria_agua.py'), SC], check=True, capture_output=True)
R['9_agua'] = 'ver som/auditoria_agua_' + SC + '.json'
# 10 · entradas/saídas naturais: maiores saltos de loudness de curto prazo (400 ms, passo 50 ms) em ambiências e música,
#      e envelopes das buzinas (subida e queda)
def saltos(x, nome):   # nível RMS em janelas de 100 ms; maior variação entre janelas vizinhas onde há som (> −60 dBFS)
    w = int(0.1 * SR); L = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-12) for i in range(0, len(x) - w, w)])
    d = np.diff(L); ok = (L[1:] > -60) & (L[:-1] > -60); d = np.where(ok, d, 0); k = np.argsort(-np.abs(d))[:4]
    return [dict(t_s=round(float((i + 1) * 0.1), 1), salto_db=round(float(d[i]), 1)) for i in sorted(k)]
amb = sf.read(f'{E}/ep01_ambiencias_{SC}.wav')[0]; mus = sf.read(f'{E}/ep01_musica_{SC}.wav')[0]
R['10_entradas_saidas'] = dict(ambiencias_maiores_saltos_100ms=saltos(amb, 'amb'), musica_maiores_saltos_100ms=saltos(mus, 'mus'),
                              buzina_maiores_saltos_100ms=saltos(sf.read(f'{E}/categorias/ep01_efeitos_buzina_{SC}.wav')[0], 'buz'))
# 11 · mono
mono = np.stack([mixw.mean(1)] * 2, 1); L, Rr = mixw[:, 0], mixw[:, 1]
R['11_mono'] = dict(estereo_lufs=round(lufs(mixw), 2), mono_lufs=round(lufs(mono), 2), perda_db=round(lufs(mixw) - lufs(mono), 2),
                    correlacao_LR=round(float(np.corrcoef(L, Rr)[0, 1]), 3), voz_10db_mono_pct=R['8_clareza_voz']['voz_10db_acima_pct'])
# 12 · final: nível dos últimos instantes no AAC (sem corte seco)
fim = {f'{t:.2f}–{t + 0.25:.2f} s': round(float(20 * np.log10(np.sqrt(np.mean(fx[int(t * SR):int((t + 0.25) * SR)] ** 2)) + 1e-12)), 1) for t in (166.5, 167.0, 167.5, 167.75)}
R['12_final'] = dict(rms_dbfs_por_trecho=fim, ultimos_20ms_dbfs=round(float(20 * np.log10(np.sqrt(np.mean(fx[-int(0.02 * SR):] ** 2)) + 1e-12)), 1))
# A × B: a diferença entre as duas mixagens deve ser SÓ a buzina (mesmo ganho de master)
dif = mixw - mixa; dw = int(0.1 * SR)
ed = np.array([np.sqrt(np.mean(dif[i:i + dw] ** 2)) for i in range(0, len(dif) - dw, dw)]); fora = np.ones(len(ed), bool)
# fora: diferenças A × B só podem estar nas buzinas, no recuo do galpão (17 s), na transição de 0:30 e nos brilhos das linhas (2:10)
for a, b in ((5.6, 11.0), (16.5, 20.0), (29.7, 43.0), (130.3, 133.7), (166.0, 168.0)): fora[int(a * 10):int(b * 10)] = False
R['AB_diferenca'] = dict(master_A_db=json.load(open(f'{A}/mix_{SS}.json'))['master_db'], master_B_db=json.load(open(f'{A}/mix_{SC}.json'))['master_db'],
                         residuo_fora_das_janelas_ajustadas_max_dbfs=round(float(20 * np.log10(ed[fora].max() + 1e-12)), 1),
                         residuo_nas_janelas_alteradas_max_dbfs=round(float(20 * np.log10(ed[~fora].max() + 1e-12)), 1),
                         narracao_dif_max_dbfs=round(float(20 * np.log10(np.abs(sf.read(f'{E}/ep01_narracao_{SS}.wav')[0] - voz).max() + 1e-20)), 1))
json.dump(R, open(os.path.join(A, 'validacao_audio_final.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1))
