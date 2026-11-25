# Ep. 02 · Arquivos definitivos (em partes)

"Como a geladeira esfria sem produzir frio?" — rodada 11, render definitivo 1080 × 1920.

O GitHub não aceita arquivos acima de 100 MB, por isso os dois arquivos definitivos estão divididos em partes de 95 MB.

## Remontar

Dentro de `episodio_02_geladeira/episodio/definitivo/`:

```bash
sha256sum -c partes.sha256
cat ep02_definitivo_1080x1920.mp4.parte* > ../ep02_definitivo_1080x1920.mp4
cat ep02_master_imagem_sem_legendas_1080.mp4.parte* > ../ep02_master_imagem_sem_legendas_1080.mp4
sha256sum ../ep02_definitivo_1080x1920.mp4 ../ep02_master_imagem_sem_legendas_1080.mp4
```

O que cada comando faz:
1. Confere as partes.
2. Remonta o episódio definitivo.
3. Remonta o master de imagem sem legendas.
4. Confere os arquivos remontados; o SHA-256 deve ser igual ao da tabela abaixo.

Para baixar só esta pasta, sem o repositório inteiro:

```bash
git clone --filter=blob:none --sparse --depth 1 -b ccr-3e676310-v0rijq https://github.com/Iron026/videos.git
cd videos
git sparse-checkout set episodio_02_geladeira/episodio/definitivo
```

## Arquivos

| Arquivo | Tamanho | SHA-256 |
|---|---|---|
| `ep02_definitivo_1080x1920.mp4` | 160,0 MB (159.996.421 bytes) | `32baf7334a461e2b00525ea0c5f27f46a06a5fcb77dd5bd28fc8fe6846efd4fa` |
| `ep02_master_imagem_sem_legendas_1080.mp4` | 161,0 MB (161.044.951 bytes) | `50cd04cfd2c9c26b3d50b0eab98e160353310f0001943d3b77e9df8d07ff21a0` |

- **Episódio definitivo:**
  - 1080 × 1920, 30 fps, 151,233 s, 4.537 quadros;
  - H.264 com CRF 17 e yuv420p, áudio AAC 192 kb/s a 48 kHz em estéreo;
  - legendas incluídas, sem o selo de revisão;
  - título nos metadados: "De Olho no Invisível · Ep. 02 · Como a geladeira esfria sem produzir frio?".
- **Master de imagem sem legendas:**
  - a mesma imagem, sem as legendas da narração;
  - rótulos, cartões de pressão, avisos e lupa continuam;
  - o áudio é o mesmo do definitivo, idêntico depois de decodificado.

## Trocar o áudio depois

A nova mixagem precisa já estar masterizada: −14 LUFS e pico verdadeiro ≤ −1,5 dBTP. Depois disso:

```bash
ffmpeg -i ep02_master_imagem_sem_legendas_1080.mp4 -i nova_mixagem.wav -map 0:v -map 1:a -c:v copy \
  -af "afade=t=out:st=151.1833:d=0.05" -c:a aac -b:a 192k -ar 48000 -t 151.2333 -movflags +faststart saida.mp4
```

Em seguida, meça de novo o AAC resultante com `som/validar_audio.py`. O pico do AAC muda de lugar quando qualquer camada muda.

Para refazer o episódio com legendas e outro áudio, use `bash episodio/montar_r11.sh final saida.mp4 nova_mixagem.wav`. Isso exige os quadros de `quadros_final/`, que não estão no git.

## Licenças

- **Narração:** plano gratuito da ElevenLabs. O episódio **não está licenciado para exploração comercial** e a atribuição é obrigatória.
- **Trilha:** "Spice Intrigue", de RomanSenykMusic, no Pixabay, sob a Pixabay Content License: uso comercial permitido e sem atribuição obrigatória, mas é proibido redistribuir o arquivo isolado, por isso ele não está no git. A conferência da licença e do Content ID na página da faixa fica com você (ver `relatorios/licencas_r10.md`). *Correção de 25/11: a versão anterior deste arquivo dizia "Mixkit" por engano.*
- **Efeitos:** ver `relatorios/licencas_r10.md`.

Nada foi publicado.
