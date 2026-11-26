"""Rodada 11 — preserva no git, SEM PERDAS, a mixagem final e os stems da validação (exceto música isolada: licença Mixkit).
 · PCM_24 → FLAC 24 bits: idêntico amostra a amostra (prova: diferença máxima = 0).
 · FLOAT (stems r9ref, pico > 0 dBFS) → ganho fixo de −6,0206 dB (×0,5, exato em ponto flutuante) → FLAC 24 bits.
   Restaurar: ler o FLAC e multiplicar por 2. Erro = só a quantização de 24 bits (medido, registrado abaixo).
Saída: som/preservado_r11/*.flac + preservado_r11.json (SHA-256 do WAV de origem, do FLAC, ganho, erro medido)."""
import os, json, hashlib
import numpy as np, soundfile as sf
A = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(A, 'preservado_r11')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
ITENS = ['audio_ep02_r11_final.wav', 'stems/ep02_voz_r9ref_f32.wav', 'stems/ep02_efeitos_r9ref_f32.wav', 'stems/ep02_mecanismo_r9ref_f32.wav',
         'stems/ep02_ambiencias_r9ref_f32.wav', 'stems/ep02_efeitos_r10_si_final.wav', 'stems/ep02_mecanismo_r10_si_final.wav']
out = dict(nota='stem de música (ep02_musica_r10_si_final.wav, Mixkit) NÃO entra no git isolado: licença proíbe redistribuir o arquivo isolado; '
                'ele está embutido na mixagem final.', itens=[])
for rel in ITENS:
    src = os.path.join(A, rel); info = sf.info(src); x, sr = sf.read(src, dtype='float64')
    ganho = 1.0 if info.subtype == 'PCM_24' else 0.5
    dst = os.path.join(D, os.path.basename(rel).replace('.wav', '.flac')); sf.write(dst, x * ganho, sr, subtype='PCM_24', format='FLAC')
    y = sf.read(dst, dtype='float64')[0] / ganho; err = float(np.abs(y - x).max())
    out['itens'].append(dict(origem=rel, formato_origem=info.subtype, sha256_origem=sha(src), flac=os.path.relpath(dst, A), sha256_flac=sha(dst),
                             bytes_flac=os.path.getsize(dst), ganho_aplicado=ganho, restaurar=f'multiplicar por {1 / ganho:g}', amostras=len(x), sr=sr,
                             erro_max_restaurado=err, erro_max_dbfs=(None if err == 0 else round(20 * np.log10(err), 1)), identico=err == 0))
    print(rel, info.subtype, 'erro', err)
json.dump(out, open(os.path.join(D, 'preservado_r11.json'), 'w'), ensure_ascii=False, indent=1)
