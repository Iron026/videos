"""Baixa de novo, das URLs oficiais, as gravações listadas em fontes_efeitos_reais.json (os arquivos não ficam no
repositório: a licença do Mixkit não permite redistribuí-los isolados). Uso: python3 episodio/som/baixar_efeitos.py"""
import os, json, subprocess
A = os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(A, 'bib', 'mixkit'), exist_ok=True)
for f in json.load(open(os.path.join(A, 'fontes_efeitos_reais.json'))):
    dst = os.path.join(A, 'bib', 'mixkit', f"{f['id']}.wav")
    if not os.path.exists(dst): subprocess.run(['curl', '-sf', '-A', 'Mozilla/5.0', '-o', dst, f['url_arquivo']], check=True); print('baixado', f['id'], f['nome'])
print('ok')
