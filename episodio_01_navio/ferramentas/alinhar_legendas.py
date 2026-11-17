"""Alinha o roteiro aprovado à narração (Whisper, timestamps por palavra), mede a fidelidade
(WER) e gera narracao/palavras.json + entrega/episodio_01_legendas.srt.
O texto das legendas é SEMPRE o do roteiro aprovado; o ASR fornece apenas os tempos."""
import json, os, re, sys, difflib, unicodedata
import numpy as np, soundfile as sf
from faster_whisper import WhisperModel

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def norm(w):
    w = unicodedata.normalize('NFD', w.lower()); w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', w)

def main(modelo):
    m = WhisperModel(modelo, device='cpu', compute_type='int8')
    audio, sr = sf.read(os.path.join(RAIZ, 'narracao/narracao.wav'), dtype='float32')
    a16 = np.interp(np.linspace(0, len(audio)-1, int(len(audio)*16000/sr)), np.arange(len(audio)), audio).astype(np.float32)
    frases = json.load(open(os.path.join(RAIZ, 'narracao/frases.json'), encoding='utf-8'))
    palavras, ref_all, hyp_all = [], [], []
    for f in frases:
        i0, i1 = int(max(0, f['inicio']-0.15)*16000), int((f['fim']+0.15)*16000)
        segs, _ = m.transcribe(a16[i0:i1], language='pt', beam_size=5, word_timestamps=True, vad_filter=False)
        hw = [w for s in segs for w in s.words]
        off = i0/16000
        hyp = [(norm(w.word), w.start+off, w.end+off) for w in hw if norm(w.word)]
        ref = f['texto'].split()
        rn = [norm(w) for w in ref]
        ref_all += rn; hyp_all += [h[0] for h in hyp]
        sm = difflib.SequenceMatcher(a=rn, b=[h[0] for h in hyp], autojunk=False)
        tempos = [None]*len(ref)
        for blk in sm.get_matching_blocks():
            for k in range(blk.size): tempos[blk.a+k] = (hyp[blk.b+k][1], hyp[blk.b+k][2])
        # interpolação para palavras não casadas (ex.: hifenização/fusões do ASR)
        known = [(i, t) for i, t in enumerate(tempos) if t]
        for i in range(len(ref)):
            if tempos[i] is None:
                prev = max([k for k in known if k[0] < i], default=(-1, (f['inicio'], f['inicio'])), key=lambda k: k[0])
                nxt = min([k for k in known if k[0] > i], default=(len(ref), (f['fim'], f['fim'])), key=lambda k: k[0])
                frac = (i - prev[0]) / (nxt[0] - prev[0])
                t = prev[1][1] + frac*(nxt[1][0]-prev[1][1]); tempos[i] = (t, t+0.2)
        for w, t in zip(ref, tempos):
            palavras.append({'palavra': w, 'inicio': round(max(t[0], f['inicio']-0.05), 3), 'fim': round(min(t[1], f['fim']+0.05), 3), 'frase': frases.index(f)})
        print(f"{'OK ' if sm.ratio() == 1 else 'DIF'} {sm.ratio():.3f} | {' '.join(h[0] for h in hyp)}")
    # WER global
    sm = difflib.SequenceMatcher(a=ref_all, b=hyp_all, autojunk=False)
    erros = sum(max(i2-i1, j2-j1) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal')
    print(f'WER aproximado: {erros}/{len(ref_all)} = {100*erros/len(ref_all):.1f}%')
    json.dump(palavras, open(os.path.join(RAIZ, 'narracao/palavras.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    # Blocos de legenda: até ~26 caracteres por linha, 2 linhas, quebra em pontuação
    blocos, atual = [], []
    for idx, p in enumerate(palavras):
        atual.append(p)
        restantes = sum(1 for q in palavras[idx+1:] if q['frase'] == p['frase'])
        txt = ' '.join(x['palavra'] for x in atual)
        fim_frase = p['palavra'][-1] in '.?!'
        prox_frase = restantes == 0
        if fim_frase or prox_frase or (restantes >= 2 and (len(txt) >= 28 or (p['palavra'][-1] == ',' and len(txt) >= 14))):
            blocos.append(atual); atual = []
    if atual: blocos.append(atual)
    def ts(t):
        ms = int(round(t*1000)); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
    legendas = []
    for i, b in enumerate(blocos):
        ini = b[0]['inicio']; fim = b[-1]['fim'] + 0.25
        if i+1 < len(blocos): fim = min(fim, blocos[i+1][0]['inicio'] - 0.02)
        legendas.append({'inicio': round(ini, 3), 'fim': round(fim, 3), 'texto': ' '.join(x['palavra'] for x in b), 'palavras': b})
    json.dump(legendas, open(os.path.join(RAIZ, 'narracao/legendas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(os.path.join(RAIZ, 'entrega/episodio_01_legendas.srt'), 'w', encoding='utf-8') as fo:
        for i, l in enumerate(legendas, 1):
            fo.write(f"{i}\n{ts(l['inicio'])} --> {ts(l['fim'])}\n{l['texto']}\n\n")
    print(len(legendas), 'legendas')

if __name__ == '__main__':
    main(sys.argv[1])
