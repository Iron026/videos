"""Rodada 13 (verificação) — preserva a mixagem B e o que é necessário para reconstruí-la, respeitando as licenças:
 · no git (FLAC 24 bits): a mixagem B completa e o stem de efeitos CC0 + camadas próprias (× 0,5: pico > 0 dBFS; restaurar × 2);
 · voz: É o stem da V9 (som/preservado_r11/ep02_voz_r9ref_f32.flac, × 0,5) com o master −0,03 dB — provado aqui, não duplicado;
 · FORA do git (licença proíbe o arquivo isolado): stem da música (Pixabay) e stem dos efeitos Mixkit. Reconstrução:
   som_r13.py + o MP3 da faixa (SHA-256 abaixo; enviado pelo usuário) + baixar_mixkit_sfx.py (SHA-256 de cada prévia no
   registro). O SHA-256 dos dois stems gerados fica registrado para provar que a reconstrução é idêntica.
Uso: python3 preservar_r13.py → som/preservado_r13/*.flac + preservado_r13.json"""
import os, json, hashlib, math
import numpy as np, soundfile as sf
A = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(A, 'preservado_r13'); os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
ST = os.path.join(A, 'stems', 'r13'); R = json.load(open(os.path.join(A, 'mix_ep02_r13.json'))); mg = R['master_r13_db']
res = dict(rodada='13 (verificação) — mixagem B, candidata; NÃO é o definitivo (aguarda aprovação auditiva)', master_r13_db=mg, arquivos={})
for nome, origem, fator in (('audio_ep02_r13B.flac', os.path.join(A, 'audio_ep02_r13_r13_teste.wav'), 1.0),
                            ('ep02_efeitos_cc0_e_proprios_r13B_x0,5.flac', os.path.join(ST, 'efeitos_cc0_e_proprios.wav'), 0.5)):
    x, sr = sf.read(origem); dst = os.path.join(OUT, nome); sf.write(dst, x * fator, sr, subtype='PCM_24')
    y = sf.read(dst)[0] / fator; err = 20 * math.log10(np.abs(y - x).max() + 1e-15)
    res['arquivos'][nome] = dict(origem=os.path.relpath(origem, A), sha256_origem=sha(origem), sha256_flac=sha(dst), fator=fator, restaurar=f'× {1 / fator:g}',
                                 erro_max_dbfs=round(err, 1), pico_origem_dbfs=round(20 * math.log10(np.abs(x).max()), 2))
v13 = sf.read(os.path.join(ST, 'voz.wav'))[0]; v9b = sf.read(os.path.join(A, 'stems', 'ep02_voz_r9ref_f32.wav'))[0]; k = float((v13 * v9b).sum() / (v9b * v9b).sum()); v9 = v9b * k; mg = round(20 * math.log10(k), 5)   # ganho exato do master (o JSON guarda arredondado)
res['voz'] = dict(e='stem da V9 × master R13', fonte_preservada='som/preservado_r11/ep02_voz_r9ref_f32.flac (× 0,5; restaurar × 2)', master_db=mg,
                  diferenca_max_dbfs=round(20 * math.log10(np.abs(v13 - v9).max() + 1e-15), 1))
res['fora_do_git'] = {}
for nome in ('musica.wav', 'efeitos_mixkit.wav'):
    p = os.path.join(ST, nome); res['fora_do_git'][nome] = dict(sha256=sha(p), motivo='licença: proibido redistribuir o item isolado (Pixabay / Mixkit)')
res['fontes_para_reconstruir'] = dict(musica_mp3='som/bib/pixabay/334566.mp3 (enviado pelo usuário)', musica_mp3_sha256=sha(os.path.join(A, 'bib', 'pixabay', '334566.mp3')),
                                      mixkit='python3 som/baixar_mixkit_sfx.py (SHA-256 de cada prévia em som/fontes_mixkit_sfx.json)',
                                      freesound='prévias CC0 em som/bib/freesound (python3 som/buscar_freesound.py; registro em som/fontes_freesound.json)',
                                      camadas_v9='CENAS_SOM=cenas_v8 CENA_R9=1 python3 som/decompor_v9.py (prova: nulo ≤ −150 dBFS)',
                                      efeitos_r10_sem_pop='GARRAFA_B5=1 MUSICA=spice_intrigue MUSICA_REL_DB=-13.5 SUF_R10=_r13_sempop python3 som/som_r10.py',
                                      mixagem='python3 som/som_r13.py  (padrões: ALVO_MUS_LU −16, SEP_DB 16, MAXD_DB −12, REL_S 0,5, PAUSA_DB 1,5, TETO_R13 −2,2, FATIAS 0)',
                                      video_de_escuta='ffmpeg -i episodio/ep02_definitivo_r12_1080x1920.mp4 -i som/audio_ep02_r13_r13_teste.wav -map 0:v -map 1:a -c:v copy -af "afade=t=out:st=151.1833:d=0.05" -c:a aac -b:a 192k -ar 48000 -t 151.2333 -movflags +faststart saida.mp4')
res['referencia_r12'] = 'som/preservado_r12/audio_ep02_r12_musica_m5.flac (intocado) + stems da R12 em som/preservado_r11 e stems/camadas_v9 (decomposição provada)'
json.dump(res, open(os.path.join(OUT, 'preservado_r13.json'), 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False, indent=1))
