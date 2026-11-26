# Ep. 02 · Arquivos definitivos R13.1 (em partes)

É a R13 com uma única mudança, pedida por você: **os avisos "Visão térmica (ilustrativa)", "Corte ilustrativo", "Tempo acelerado", "Fluxo desacelerado" e "Câmera lenta" foram retirados**.

- Ficam "Canal ampliado (esquema)", no D4 e no F2, e o aviso da lupa, no G3.
- Só mudou o desenho dos avisos. Rótulos, cartões de pressão, legendas, imagem 3D e áudio são idênticos à R13.

**Situação:** aprovação técnica feita. **Falta a sua aprovação final.** Nada foi publicado.

A R13 continua em `../definitivo_r13/`, e a R12 em `../definitivo_r12/`.

## Remontar

```
cd episodio/definitivo_r13_1
sha256sum -c partes.sha256
cat ep02_definitivo_r13_1_1080x1920.mp4.parte* > ../ep02_definitivo_r13_1_1080x1920.mp4
cat ep02_master_imagem_sem_legendas_r13_1_1080.mp4.parte* > ../ep02_master_imagem_sem_legendas_r13_1_1080.mp4
```

| Arquivo | SHA-256 |
|---|---|
| `ep02_definitivo_r13_1_1080x1920.mp4` | `1c7cdd5bd4300b4c035c3328f996c7aff1be8c0572c985552c556ee95349b7f5` |
| `ep02_master_imagem_sem_legendas_r13_1_1080.mp4` | `67eb850e73801555862146dfa86d08a4f4584804ea826ec5a77204fb63850cd3` |

Montagem: `bash episodio/montar_r13_1.sh` (com `SEM_LEGENDAS=1` para o master).
