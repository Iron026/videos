# Episódio 02 · Como a geladeira esfria sem produzir frio?

Estrutura independente; o Ep. 01 não foi alterado (procedência dos arquivos reaproveitados: `motor/PROCEDENCIA.md`).
**Nada publicado.** Narração aprovada: **ainda não existe** (tempos provisórios calibrados na voz do Ep. 01).

| Pasta | Conteúdo |
|---|---|
| `roteiro/` | Roteiro oficial preservado (SHA-256), texto sem tags, tempos provisórios por palavra (`tempos_provisorios.py`) |
| `ciencia/` | Modelo didático do ciclo (R600a, CoolProp), testes científicos, diagrama P–h, validação científica e fontes |
| `decupagem/` | 39 planos ancorados em palavras (`planos.py`) e decupagem cinematográfica (`decupagem_ep02_v1.md`) |
| `config/producao.json` | Configuração ÚNICA de render (animatic, revisão, final) |
| `blender/` | Modelo (geladeira, cozinha, circuito, compressor), materiais do Ep. 02, linha do tempo (`episodio02.py`), testes de cena |
| `motor/` | Fork do motor Three.js r170 (`render3.js`): visão térmica, fluido, calor, trabalho, corte |
| `episodio/` | Render por plano, folha de contato, montagem (`montar_ep02.py`) |
| `relatorios/` | Testes, folhas de contato e relatórios de revisão |

## Reproduzir
```bash
pip install --target /caminho/bpy bpy==5.1.2 && pip install CoolProp scipy matplotlib
(cd motor && npm install)                                  # three 0.170.0
python3 ciencia/modelo_ciclo.py && python3 ciencia/testes_ciclo.py
python3 roteiro/tempos_provisorios.py && python3 decupagem/planos.py
PYTHONPATH=/caminho/bpy python3 blender/testes_cena.py
PYTHONPATH=/caminho/bpy python3 blender/episodio02.py      # exporta os 39 planos
python3 episodio/render_planos.py animatic                 # um processo por vez
python3 episodio/montar_ep02.py animatic
```
Quando a narração aprovada chegar: alinhar palavra a palavra → `roteiro/palavras.json`; todos os tempos se recalculam.
