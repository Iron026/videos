"""Registro de configuração e integridade do Ep. 01 definitivo (gera registro_final_ep01.json e .md).
Resume o manifesto do render (quadros por segmento, identificadores de configuração, correções locais, migração com evidência,
semelhança mínima com a revisão aprovada) e calcula o SHA-256 das entregas e das fontes que as determinam.
Uso: python3 episodio/registro_final.py <final.mp4> [master_sem_legendas.mp4]"""
import os, sys, json, hashlib, subprocess, time
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
final = sys.argv[1]; master = sys.argv[2] if len(sys.argv) > 2 else None
man = json.load(open(os.path.join(A, 'quadros_final', '_manifesto.json')))
segs = {}
for s, v in man['segmentos'].items():
    q = v['quadros']; sg = [r.get('ssim_grosso', 1) for r in q.values()]
    segs[s] = dict(quadros=len(q), esperados=v['n'], cena=v['cena'], configs=sorted({r['config'] for r in q.values()}),
                   ssim_grosso_min=round(min(sg), 4), rerenders=sum(1 for r in q.values() if 'rerender' in r))
probe = lambda f: json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size,bit_rate:format_tags=title:stream=codec_name,width,height,r_frame_rate,sample_rate,channels', '-of', 'json', f], capture_output=True, text=True).stdout)
fontes = {k: os.path.join(R, v) for k, v in {
    'audio_mix_aprovado': 'episodio/audio_ep01_refinado_buzina.wav', 'narracao_original_mp3': 'voz/narracao_ep01/Narração ep 1.mp3',
    'narracao_trabalho_wav': 'voz/narracao_ep01/trabalho/narracao_48k.wav', 'palavras_legendas': 'voz/narracao_ep01/trabalho/palavras.json',
    'render2_js': 'motores/tempo_real_v2/render2.js', 'render_anim_mjs': 'motores/tempo_real_v2/render_anim.mjs', 'render_final_py': 'episodio/render_final.py',
    'montar_ep01_py': 'episodio/montar_ep01.py', 'grade_ep01_py': 'episodio/grade_ep01.py', 'trocar_audio_py': 'episodio/trocar_audio.py', 'som_refinado_py': 'episodio/som/som_refinado.py'}.items()}
reg = dict(gerado=time.strftime('%Y-%m-%d %H:%M:%S'),
           arquivo_final=dict(caminho=os.path.relpath(final, R), sha256=sha(final), **probe(final)),
           master_sem_legendas=(dict(caminho=os.path.relpath(master, R), sha256=sha(master), **probe(master)) if master else None),
           render=dict(config_id=man['config_id'], config=man['config'], segmentos=segs, total_quadros=sum(v['quadros'] for v in segs.values()),
                       migracoes=man.get('migracoes', [])),
           fontes={k: dict(caminho=os.path.relpath(p, R), sha256=sha(p)) for k, p in fontes.items() if os.path.exists(p)},
           licenca_narracao='ElevenLabs, plano gratuito: sem licença para exploração comercial (voz/LICENCA_NARRACAO.md)')
json.dump(reg, open(os.path.join(A, 'registro_final_ep01.json'), 'w'), ensure_ascii=False, indent=1)
md = ['# Ep. 01 · Registro de configuração e integridade (arquivo definitivo)', '', f'Gerado em {reg["gerado"]}.', '',
      '| Arquivo | SHA-256 |', '|---|---|', f'| `{reg["arquivo_final"]["caminho"]}` | `{reg["arquivo_final"]["sha256"]}` |']
if master: md.append(f'| `{reg["master_sem_legendas"]["caminho"]}` | `{reg["master_sem_legendas"]["sha256"]}` |')
md += [f'| `{v["caminho"]}` | `{v["sha256"]}` |' for v in reg['fontes'].values()]
md += ['', f'**Render:** configuração `{man["config_id"]}` · `{man["config"]["consulta"]}` · correções locais: {man["config"].get("por_segmento", {})} · {reg["render"]["total_quadros"]} quadros', '',
       '| Segmento | Quadros | Cena (hash) | Configuração | SSIM grosso mín. | Re-renders |', '|---|---|---|---|---|---|']
md += [f'| s{s} | {v["quadros"]}/{v["esperados"]} | `{v["cena"]}` | {", ".join(v["configs"])} | {v["ssim_grosso_min"]} | {v["rerenders"]} |' for s, v in segs.items()]
open(os.path.join(A, 'registro_final_ep01.md'), 'w').write('\n'.join(md) + '\n'); print('ok registro_final_ep01.json / .md')
