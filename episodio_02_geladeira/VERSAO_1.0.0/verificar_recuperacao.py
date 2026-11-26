"""Ep. 02 v1.0.0 — prova de recuperação a partir do repositório (funciona num checkout limpo; não precisa de nada fora do git).
 1. confere o SHA-256 de cada parte dos MP4 (definitivo e master sem legendas);
 2. remonta os MP4 numa pasta temporária e confere o SHA-256 dos arquivos inteiros;
 3. confere o arquivo de cenas, extrai e recalcula o hash de CADA cena (o mesmo registrado nos manifestos de render);
 4. confere o FLAC da mixagem final e o arquivo de manifestos de render.
Uso: python3 episodio_02_geladeira/VERSAO_1.0.0/verificar_recuperacao.py [--git-ref origin/<ramo>]
     (com --git-ref, lê TUDO direto dos objetos do git desse ref — prova de que o remoto basta)"""
import os, sys, json, hashlib, tempfile, tarfile, subprocess
V = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(V); RAIZ = os.path.dirname(R)
ref = sys.argv[sys.argv.index('--git-ref') + 1] if '--git-ref' in sys.argv else None
M = json.load(open(os.path.join(V, 'manifesto_v1.0.0.json')))
def ler(rel):
    if ref: return subprocess.run(['git', '-C', RAIZ, 'show', f'{ref}:episodio_02_geladeira/{rel}'], capture_output=True, check=True).stdout
    return open(os.path.join(R, rel), 'rb').read()
sha = lambda b: hashlib.sha256(b).hexdigest()
res = {}; tmp = tempfile.mkdtemp(prefix='ep02_v1_')
partes = {}
for rel, h in M['partes'].items():
    b = ler(rel); partes[rel] = b; res[rel] = sha(b) == h
for alvo, h in M['entregaveis'].items():
    nome = os.path.basename(alvo); ps = sorted(p for p in partes if os.path.basename(p).startswith(nome + '.parte'))
    dst = os.path.join(tmp, nome)
    with open(dst, 'wb') as f:
        for p in ps: f.write(partes[p])
    res[f'remontado {nome}'] = sha(open(dst, 'rb').read()) == h; os.remove(dst)
b = ler('VERSAO_1.0.0/cenas_definitivo_ep02.tar.xz'); res['arquivo de cenas'] = sha(b) == M['cenas']['sha256']
arq = os.path.join(tmp, 'cenas.tar.xz'); open(arq, 'wb').write(b); tarfile.open(arq).extractall(tmp, filter='data')
for c, h in M['cenas']['hash_por_cena'].items():
    d = os.path.join(tmp, 'cenas', c); hh = hashlib.sha256()
    for f in sorted(os.listdir(d)): hh.update(f.encode()); hh.update(open(os.path.join(d, f), 'rb').read())
    res[f'cena {c}'] = hh.hexdigest()[:16] == h
res['FLAC da mixagem final'] = sha(ler('som/preservado_r13c/audio_ep02_r13C_final.flac')) == M['audio']['som/preservado_r13c/audio_ep02_r13C_final.flac']
res['manifestos de render'] = sha(ler('VERSAO_1.0.0/manifestos_render_ep02.tar.xz')) == M['manifestos_render']['sha256']
subprocess.run(['rm', '-rf', tmp])
falhas = [k for k, v in res.items() if not v]
print(json.dumps(dict(fonte=ref or 'cópia de trabalho', verificados=len(res), falhas=falhas, tudo_recuperavel=not falhas), ensure_ascii=False, indent=1))
sys.exit(1 if falhas else 0)
