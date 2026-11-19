"""Rastreia vozes humanas nas gravações candidatas (faster-whisper com VAD): uma gravação 'de água' com gente falando
não serve para um evento físico. Marca segmentos com fala provável."""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
m = json.load(open('candidatos_mixkit.json'))
mod = WhisperModel(sys.argv[1] if len(sys.argv) > 1 else 'small', device='cpu', compute_type='int8')
for x in m:
    a, sr = sf.read(x['arquivo_local'].replace('som/', ''), always_2d=True); a = resample_poly(a.mean(1), 16000, sr).astype(np.float32)
    segs, info = mod.transcribe(a, vad_filter=True, beam_size=1, condition_on_previous_text=False)
    fala = [(round(s.start, 1), round(s.end, 1), s.text.strip()) for s in segs if s.no_speech_prob < 0.4 and s.avg_logprob > -0.9 and len(s.text.strip()) > 2]
    x['voz_detectada'] = fala
    if fala: print(x['id'], x['titulo'], fala[:3], flush=True)
json.dump(m, open('candidatos_mixkit.json', 'w'), ensure_ascii=False, indent=1)
print('fim')
