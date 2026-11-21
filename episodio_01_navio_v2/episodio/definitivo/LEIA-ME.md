# Ep. 01 · Arquivos definitivos (em partes)

O GitHub não aceita arquivos acima de 100 MB, por isso os dois arquivos definitivos estão divididos em partes de 95 MB.

## Remontar

Dentro de `episodio_01_navio_v2/episodio/definitivo/`:

```bash
sha256sum -c partes.sha256
cat ep01_definitivo_1080x1920.mp4.parte* > ../ep01_definitivo_1080x1920.mp4
cat ep01_master_imagem_sem_legendas_1080.mp4.parte* > ../ep01_master_imagem_sem_legendas_1080.mp4
sha256sum ../ep01_definitivo_1080x1920.mp4 ../ep01_master_imagem_sem_legendas_1080.mp4
```

O que cada comando faz:
1. Confere as partes.
2. Remonta o episódio definitivo.
3. Remonta o master de imagem sem legendas.
4. Confere os arquivos remontados.

## Arquivos

| Arquivo | Tamanho | SHA-256 |
|---|---|---|
| `ep01_definitivo_1080x1920.mp4` | 141,8 MB | `5640980a5627f9bec4bc8c9125645501aa94b53681e1fad5d628e3394e8e2491` |
| `ep01_master_imagem_sem_legendas_1080.mp4` | 196,6 MB | `a5d0dd2e14bf3918512184201919f4fce3029a398fec7c332eb1fd4c62eae188` |

- **Episódio definitivo:**
  - 1080 × 1920, 30 fps, 168,000 s, 5.040 quadros;
  - H.264, com o áudio aprovado em AAC 48 kHz;
  - legendas incluídas, sem o selo de revisão.
- **Master de imagem sem legendas:** a mesma imagem, para trocar o áudio sem renderizar de novo.

## Trocar o áudio depois

```bash
python3 episodio/trocar_audio.py <nova_mixagem.wav> <saida.mp4> episodio/ep01_master_imagem_sem_legendas_1080.mp4
```

O script detecta o master 1080 e aplica:
- a escala de legendas do perfil final;
- CRF 17;
- o controle de loudness e de pico verdadeiro do AAC final, em −14 LUFS e ≤ −1,6 dBTP.

## Licença da narração

A narração vem do plano gratuito da ElevenLabs. O episódio **não está licenciado para exploração comercial** (ver `voz/LICENCA_NARRACAO.md`).
