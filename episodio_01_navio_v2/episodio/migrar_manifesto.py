"""Migração do manifesto do render definitivo após uma mudança INERTE no render2.js (parâmetro novo desligado por padrão).
Para cada segmento concluído sem correção local: re-renderiza 3 quadros de amostra (início, meio, fim) com o código atual e
compara com os quadros registrados. Só se TODOS ficarem dentro da variação normal entre renderizações idênticas (diferença média
< 0,5 e < 2.000 pixels com diferença > 20, em 2,07 milhões) os registros do segmento passam para o identificador atual; a
evidência fica no manifesto (chave 'migracoes'). Segmentos com correção local (SEG_EXTRA) não migram: são renderizados de novo.
Uso: python3 episodio/migrar_manifesto.py"""
import os, sys, json, time, subprocess, numpy as np, importlib.util
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motores', 'tempo_real_v2'); TMP = os.path.join(A, 'quadros_final_descartados', '_migracao')
src = open(os.path.join(A, 'render_final.py')).read().split("os.makedirs(SAIDA, exist_ok=True)\nman =")[0]   # só as definições, sem executar o render
rf = {'__file__': os.path.join(A, 'render_final.py'), '__name__': 'rf'}; exec(compile(src, 'render_final.py', 'exec'), rf)
man = json.load(open(rf['MAN'])); antigo = man.get('config_id'); novo = rf['CID']
ev = dict(data=time.strftime('%Y-%m-%d %H:%M:%S'), de=antigo, para=novo, motivo='render2.js: parâmetro fantoff (desligado por padrão) acrescentado; sem efeito fora do s08a', segmentos={})
for seg, ms in man['segmentos'].items():
    regs = ms['quadros']
    if seg in rf['SEG_EXTRA'] or not regs or all(r.get('config') == rf['cid'](seg) for r in regs.values()): continue
    qs = sorted(int(q) for q in regs); amostras = [qs[0], qs[len(qs) // 2], qs[-1]]; res = []
    for q in amostras:
        subprocess.run(['node', 'render_anim.mjs', f'cena=../../episodio/cenas/s{seg}/&{rf["Q"]}', os.path.relpath(TMP, MOTOR), '1', str(q), str(q)], cwd=MOTOR, capture_output=True)
        a = np.asarray(Image.open(os.path.join(TMP, f'q{q:04d}.jpg'))).astype(np.float32); b = np.asarray(Image.open(os.path.join(rf['SAIDA'], f's{seg}', f'q{q:04d}.jpg'))).astype(np.float32)
        d = np.abs(a - b).max(2); res.append(dict(quadro=q, dif_media=round(float(d.mean()), 3), px_dif_maior_20=int((d > 20).sum())))
        os.remove(os.path.join(TMP, f'q{q:04d}.jpg'))
    ok = all(r['dif_media'] < 0.5 and r['px_dif_maior_20'] < 2000 for r in res)
    ev['segmentos'][seg] = dict(amostras=res, equivalente=ok, quadros=len(regs))
    if ok:
        for r in regs.values(): r['config'] = rf['cid'](seg)
    print(seg, 'equivalente' if ok else 'NÃO equivalente', res, flush=True)
man.setdefault('migracoes', []).append(ev); man['config'], man['config_id'] = rf['CONFIG'], novo
t = rf['MAN'] + '.tmp'; json.dump(man, open(t, 'w'), ensure_ascii=False); os.replace(t, rf['MAN'])
print('migração registrada', antigo, '→', novo)
