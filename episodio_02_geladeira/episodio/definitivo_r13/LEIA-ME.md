# Ep. 02 · Arquivos definitivos R13 (em partes)

"Como a geladeira esfria sem produzir frio?" — rodada 13, montagem definitiva em 1080 × 1920.

**Situação:** aprovação técnica feita. **Falta a sua aprovação final do vídeo completo.** Nada foi publicado.

A R12 continua intacta em `../definitivo_r12/`, e a R11 em `../definitivo/`.

## Remontar

```
cd episodio/definitivo_r13
sha256sum -c partes.sha256
cat ep02_definitivo_r13_1080x1920.mp4.parte* > ../ep02_definitivo_r13_1080x1920.mp4
cat ep02_master_imagem_sem_legendas_r13_1080.mp4.parte* > ../ep02_master_imagem_sem_legendas_r13_1080.mp4
sha256sum ../ep02_definitivo_r13_1080x1920.mp4 ../ep02_master_imagem_sem_legendas_r13_1080.mp4   # compare com inteiros.sha256
```

| Arquivo | SHA-256 |
|---|---|
| `ep02_definitivo_r13_1080x1920.mp4` | `bd3a33d2690a05d14b507aadbdf7dd7052628cdafee8b0b8a6c5a053c708124c` |
| `ep02_master_imagem_sem_legendas_r13_1080.mp4` | `76da28ee244275025779f9a076b19b3b32e1c675bfaa36ed6ab306d916889be3` |

## O que mudou em relação à R12

Só o que você aprovou:

1. **Som (R13C final):**
   - música Spice Intrigue na mixagem B;
   - ruído contínuo removido;
   - efeitos retirados em 0:14, 1:12 e 1:48;
   - revelação de 0:33 discreta, sem o impacto cinematográfico;
   - passos de 1:55 e batida da porta de 0:29,6 mais baixos, pela perspectiva da câmera.
2. **E3 (1:18–1:23):** z-fighting corrigido em duas junções:
   - bobina × estator, com as faces de contato retiradas;
   - bloco do cilindro × placa de válvulas, com folga de 0,02 mm.
   - Só os 160 quadros do E3 foram re-renderizados.
3. **Quadros repetidos** por empate de arredondamento na montagem, corrigidos no A1, B7, H1 e I1 (125 quadros, sem render 3D).

A entrada do E3 manteve a fusão.

Detalhes em `relatorios/relatorio_r13_definitivo.md`.
