# Ep. 02 · Arquivos definitivos R12 (em partes)

"Como a geladeira esfria sem produzir frio?" — rodada 12, render definitivo 1080 × 1920.

Esta é a versão **atual**. A entrega anterior, a R11, continua intacta em `../definitivo/` para comparação.

## O que mudou em relação à R11

Só duas coisas mudaram, e ambas foram pedidas:

1. **A água da garrafa não fica mais branca de repente em 1:53.**
   - **Causa:** o three.js decide a ordem em que desenha os objetos transparentes pela profundidade do centro de cada um. Com a câmera em movimento, a garrafa e a prateleira de vidro trocavam de ordem de um quadro para o outro, e a mistura dos dois materiais mudava de uma vez.
   - **Correção:** a ordem fica fixa do primeiro ao último quadro de cada plano. A varredura achou cinco trocas com sobreposição na tela, e a correção foi aplicada só nos três planos em que ela muda a imagem. No C2 e no F1, a troca existe mas não muda a imagem, e eles ficaram como aprovados. Planos corrigidos:
     - H2, a partir do quadro 48 da cena;
     - C4, a partir do quadro 52;
     - H1, a partir do quadro 75.
   - **Reaproveitamento:** os quadros anteriores à troca já tinham a ordem certa e foram reaproveitados, com prova.
2. **Música +5 dB**, a mixagem escolhida no A/B. Efeitos, mecanismo e ambiências não mudaram, e nenhum som foi trocado.

Comparação medida entre o definitivo R12 e o R11, quadro a quadro em resolução cheia:

| Quadros | Quantidade |
|---|---|
| Idênticos byte a byte | 3.914 de 4.537 |
| Diferentes nos planos corrigidos ou nas fusões que os misturam | 284 |
| Diferentes só pelo codificador (média ≤ 1,6 de 255, até o próximo quadro-chave) | 339 |
| Diferenças inesperadas | **0** |

Detalhes em `relatorios/relatorio_r12_definitivo.md`.

## Remontar

Dentro de `episodio_02_geladeira/episodio/definitivo_r12/`:

```bash
sha256sum -c partes.sha256
cat ep02_definitivo_r12_1080x1920.mp4.parte* > ../ep02_definitivo_r12_1080x1920.mp4
cat ep02_master_imagem_sem_legendas_r12_1080.mp4.parte* > ../ep02_master_imagem_sem_legendas_r12_1080.mp4
sha256sum ../ep02_definitivo_r12_1080x1920.mp4 ../ep02_master_imagem_sem_legendas_r12_1080.mp4
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
git sparse-checkout set episodio_02_geladeira/episodio/definitivo_r12
```

## Arquivos

| Arquivo | Tamanho | SHA-256 |
|---|---|---|
| `ep02_definitivo_r12_1080x1920.mp4` | 160,0 MB (160.040.293 bytes) | `53cb24f5abaf06806f6f50d05708e0d69171a95f29fc62e8c0aa96e0ac6aa6b9` |
| `ep02_master_imagem_sem_legendas_r12_1080.mp4` | 161,2 MB (161.177.250 bytes) | `92a178704c6ede957e1531ab996b0deacdc6e8c4c26eb0ba27c510f547fb1c93` |

- **Episódio definitivo:**
  - 1080 × 1920, 30 fps, 151,233 s, 4.537 quadros;
  - H.264 com CRF 17 e yuv420p, áudio AAC 192 kb/s a 48 kHz em estéreo;
  - legendas incluídas, sem o selo de revisão;
  - título nos metadados: "De Olho no Invisível · Ep. 02 · Como a geladeira esfria sem produzir frio?".
- **Master de imagem sem legendas:**
  - a mesma imagem, sem as legendas da narração;
  - rótulos, cartões de pressão, avisos e lupa continuam;
  - o áudio é o mesmo do definitivo.
- **Áudio dos dois:** é idêntico, depois de decodificado, ao do teste 540 com a música +5 dB que você aprovou.
  - Decodificado: `583b3d4322a137ba…`.
  - Mixagem sem perdas em `som/preservado_r12/audio_ep02_r12_musica_m5.flac`.

## Trocar o áudio depois

A nova mixagem precisa já estar masterizada: −14 LUFS e pico verdadeiro ≤ −1,5 dBTP. Depois disso:

```bash
ffmpeg -i ep02_master_imagem_sem_legendas_r12_1080.mp4 -i nova_mixagem.wav -map 0:v -map 1:a -c:v copy \
  -af "afade=t=out:st=151.1833:d=0.05" -c:a aac -b:a 192k -ar 48000 -t 151.2333 -movflags +faststart saida.mp4
```

Em seguida, meça de novo o AAC resultante com `som/validar_audio.py`. O pico do AAC muda de lugar quando qualquer camada muda.

Para refazer o episódio com legendas e outro áudio, use:

```bash
bash episodio/montar_r11.sh final saida.mp4 nova_mixagem.wav
```

Isso exige os quadros de `quadros_final/`, que não estão no git.

## Licenças

- **Narração:** plano gratuito da ElevenLabs. O episódio **não está licenciado para exploração comercial**, e a atribuição é obrigatória.
- **Trilha:** "Spice Intrigue", de RomanSenykMusic, no Pixabay, sob a Pixabay Content License.
  - Uso comercial permitido e sem atribuição obrigatória.
  - É proibido redistribuir o arquivo isolado, por isso ele não está no git.
  - A conferência da licença e do Content ID na página da faixa fica com você (ver `relatorios/licencas_r10.md`).
- **Efeitos:** ver `relatorios/licencas_r10.md`.

Nada foi publicado.
