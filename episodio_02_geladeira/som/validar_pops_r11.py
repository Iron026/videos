"""Rodada 11 — eventos de 'destaque' (pouso da garrafa + 5 pops de apresentação) no ÁUDIO FINAL (medida, não escuta):
 · inteligibilidade no instante de cada evento: voz − resto na faixa do celular (mono, 350 Hz–7 kHz), janela [t−0,02; t+0,20] s
   e ±0,5 s, com os stems da mixagem validada (STEMS_VOZ / STEMS_RESTO, mesmos do validar_audio.py);
 · nível do evento em relação à voz (alvo da mixagem: −9 dB nos pops, −12 dB no pouso), lido do registro da mixagem;
 · fidelidade do AAC no instante do evento: correlação e diferença de nível AAC × WAV aprovado na mesma janela (o AAC reproduz o pop);
 · atraso global AAC × WAV (correlação cruzada).
Uso: python3 validar_pops_r11.py <video.mp4> <audio.wav> <mix.json>  → relatorios/testes_r10/validacao_pops_r11.json"""
import os, sys, json, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, correlate
A = os.path.dirname(os.path.abspath(__file__)); SR = 48000
video, wav, mixj = sys.argv[1:4]
r = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
aac = np.frombuffer(r, np.float32).astype(np.float64).reshape(-1, 2); ref, sr = sf.read(wav); assert sr == SR
cel = butter(4, [350, 7000], 'bandpass', fs=SR, output='sos'); rms = lambda x: float(np.sqrt(np.mean(x ** 2)) + 1e-12); db = lambda x: 20 * np.log10(x)
st = os.path.join(A, 'stems')
voz = sf.read(os.path.join(st, os.environ['STEMS_VOZ']))[0].mean(1)
resto = sum(sf.read(os.path.join(st, f))[0].mean(1) for f in os.environ['STEMS_RESTO'].split(','))
vc, rc = sosfiltfilt(cel, voz), sosfiltfilt(cel, resto)
# atraso global (60 s centrais, mono)
a0, a1 = 40 * SR, 100 * SR; m1, m2 = aac[a0:a1].mean(1), ref[a0:a1].mean(1)
cc = correlate(m1, m2, mode='full', method='fft'); lag = int(np.argmax(cc) - (len(m2) - 1))
ev = [e for e in json.load(open(mixj))['eventos'] if e.get('stem') == 'destaque']; out = []
for e in ev:
    t = e['t']; linha = dict(t=t, uso=e['uso'], alvo_rel_voz_db=e['rel_voz_celular_db'])
    for nome, (u0, u1) in dict(evento=(t - 0.02, t + 0.20), mais_menos_0_5s=(t - 0.5, t + 0.5)).items():
        a, b = int(u0 * SR), int(u1 * SR); v, x = rms(vc[a:b]), rms(rc[a:b])
        linha[f'voz_menos_resto_{nome}_db'] = round(db(v) - db(x), 1) if v > 1e-4 else None
        if nome == 'evento' and v <= 1e-4: linha['obs'] = 'sem fala na janela do evento'
    a, b = int((t - 0.02) * SR), int((t + 0.20) * SR); w1, w2 = aac[a + lag:b + lag].mean(1), ref[a:b].mean(1)
    linha['aac_x_wav_corr'] = round(float(np.corrcoef(w1, w2)[0, 1]), 4); linha['aac_menos_wav_db'] = round(db(rms(w1)) - db(rms(w2)), 2)
    out.append(linha)
res = dict(video=os.path.basename(video), wav=os.path.basename(wav), atraso_aac_amostras=lag, stems=dict(voz=os.environ['STEMS_VOZ'], resto=os.environ['STEMS_RESTO']), eventos=out,
           nota='voz − resto ≥ 6 dB na janela do evento = a fala continua dominante na faixa do celular; o evento fica abaixo da voz por construção (alvo −9/−12 dB)')
res['aprovado_tecnico'] = all((o['voz_menos_resto_evento_db'] is None or o['voz_menos_resto_evento_db'] >= 6) and o['aac_x_wav_corr'] >= 0.98 for o in out)
p = os.path.join(A, '..', 'relatorios', 'testes_r10', f'validacao_pops_r11{os.environ.get("SUF_VALIDACAO", "")}.json')   # SUF_VALIDACAO (R12): não sobrescreve o registro aprovado
json.dump(res, open(p, 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1))
