# Ep. 02 · R13: verificação final da mixagem B (para sua escuta)

**Arquivo para ouvir:** `episodio/previas_r13/ep02_r13B_escuta_1080x1920.mp4`, o episódio inteiro.

- A imagem é a do definitivo R12, copiada sem recodificar: o MD5 do fluxo de vídeo é o mesmo (`c0342ad0…`).
- São 4.537 quadros e 151,233 s.
- **Não é o definitivo:** aguarda a sua aprovação auditiva.
- Eu meço, não escuto. **Nada foi publicado.**

## 1. Música no alto-falante de celular

Simulei um alto-falante de celular: mono, praticamente sem graves abaixo de 450 Hz.

**Como medi:** em 13 bandas de 1/3 de oitava, de 50 em 50 ms durante a fala, contei se a música aparece em pelo menos 2 bandas sem ser mascarada pela voz e pelos efeitos.

| Versão (mesmo volume total) | Música perceptível na fala | Inteligibilidade (índice tipo SII), mediana / p5 | Voz − resto, p5 |
|---|---|---|---|
| R12 | 23 % | 0,886 / 0,561 | 10,3 dB |
| **B** | **34 %** | **0,917 / 0,527** | **10,7 dB** |
| B + EQ dinâmica por banda | 43 % | 0,886 / 0,470 | 9,9 dB |
| B + EQ por banda + realce acima de 2 kHz | 47 % | 0,869 / 0,453 | 9,8 dB |
| B + EQ por banda conservadora (protege 24–30 dB) | 32–36 % | 0,907–0,919 / 0,502–0,518 | 10,5–10,6 dB |

**Conclusão:**
- A EQ dinâmica por banda só deixa a música mais presente no celular **cobrando clareza da voz**: o p5 cai abaixo de 10 e o índice de inteligibilidade baixa.
- Nas versões que preservam a voz, o ganho fica em ±2 pontos.
- **Mantive a B, sem subir o volume.**
- No celular, a música aparece em cerca de 1/3 da fala e fica clara nas transições, nas revelações e no encerramento.
- Nos 5 % de quadros mais difíceis, o índice de inteligibilidade fica um pouco abaixo da R12 (0,527 contra 0,561), porque agora há música onde antes não havia. A mediana é melhor e o critério do projeto passa.

## 2. Emendas da música

A versão anterior tinha dois problemas:
- **1:43,6:** repetia imediatamente os 8 compassos que você acabou de ouvir.
- **2:04,0:** repetia 1 compasso no meio de uma frase de 4.

A faixa é construída em **frases de 4 compassos**: a semelhança harmônica com 4 compassos antes é 0,84; com 1 compasso antes, 0,72. Por isso a emenda foi refeita:

- **8 compassos (17–24 da faixa) entram no início do compasso 29**, na mesma posição da frase.
- **As emendas agora ficam em 1:20,5 e 1:41,0.** Ambas ficam dentro da variação que a própria música tem de um compasso para o outro:

| | 1:20,5 | 1:41,0 | Natural da faixa |
|---|---|---|---|
| Salto espectral | 244 | 159 | mediana 202, p90 293 |
| Continuidade harmônica | 0,76 | 0,64 | mediana 0,72, p10 0,59 |
| Salto de nível | −1,7 dB | −1,3 dB | até 2,1 dB (p90) |
| Batida | dentro da variação natural | dentro da variação natural | — |

- **Repetição:** o trecho de 20 s volta 10 s depois da primeira vez (primeiro em 0:49,9–1:10,4, de novo em 1:20,5–1:41,0), com outra passagem no meio e em cenas diferentes. É uma reprise de seção, como a faixa já faz por si.
  - Uma fonte mais distante (a 20 s) piora a costura: −2,6 dB de nível e harmonia no limite.
- **Nenhum compasso isolado do final emenda bem**, então não há mais o "+1 compasso". O **acorde final agora cai aos 147,21 s, sobre "não cria frio."**, e ressoa sob "Ela dá um destino ao calor.", apagando com a última palavra.
- **Ouça em 1:20,5, 1:41,0 e no final.**

## 3. Efeitos

- **O relé do E2 saiu.** A curva que liga aos 75,37 s é só a visualização do trabalho elétrico (pulsos violeta); o compressor já funcionava, como a própria mixagem original assumia.
  - Agora o zumbido **já está presente quando a câmera chega** ao compressor (E1, de 71,4 a 73,4 s).
  - Ele segue contínuo no E2 e no E3 e sai com a câmera no E4.
- **Dois acentos retirados por excesso:**
  - o sopro do B3, que vinha 1,1 s depois do impacto do "não fabrica frio.";
  - o whoosh C4 → D1, que vinha 2 s antes do pop do rótulo "Evaporador".
- **Ficam 12 acentos em 151 s:** transição do rosto, 2 impactos de revelação, o pulso do circuito, o fluxo discreto no tubo, 5 apresentações e 2 movimentos de câmera estruturais. Os sons dos mecanismos só tocam quando o mecanismo está na tela.
- **26 eventos verificados no AAC final:**
  - voz sobre a fala de **7,4 a 23,1 dB** acima do resto (regra ≥ 6);
  - pico a **−1 a +9 ms** da ação (um quadro tem 33 ms);
  - AAC × WAV com correlação ≥ 0,998 e atraso 0.

## 4. Loudness, pico e inteligibilidade, medidos no AAC do arquivo de escuta

| Medida | B | R12 | Meta |
|---|---|---|---|
| Loudness | **−14,15 LUFS** | −14,09 | −14 |
| Pico verdadeiro | **−1,87 dBTP** | −1,52 | ≤ −1,5 |
| Voz − resto no celular (p5 / mediana / pior janela) | **10,7 / 23,4 / −4,0 dB** | 10,3 / 23,3 / −8,7 | p5 ≥ 10 |
| Perda em mono | −0,02 dB | −0,02 | ~0 |
| Último 0,5 s | **−71 dBFS** | −45,6 | silêncio |

O teto do limitador baixou 0,2 dB: em −2,0, o AAC saía com −1,53 dBTP, margem de só 0,03 dB.

## 5. Preservação

- **Imagem, narração, legendas, animações e tempos:** intocados. Não houve render 3D.
- **Referência R12:** `som/preservado_r12/audio_ep02_r12_musica_m5.flac`, intacta (SHA-256 `5c3b593e…`).
- **Mixagem B:** `som/preservado_r13/audio_ep02_r13B.flac` (erro −144,5 dBFS).
- **Stem de efeitos CC0 + camadas próprias:** em FLAC × 0,5 (restaurar × 2).
- **Voz:** é o stem da V9 com master −0,03171 dB (resíduo −144,7 dBFS), já preservado na R11.
- **Fora do git, por licença:** o stem da música (Pixabay) e o de efeitos Mixkit, porque é proibido redistribuir o item isolado. O SHA-256 de cada um está registrado, e eles são reconstruídos por `som/som_r13.py` a partir das fontes.
  - O MP3 da faixa, que você enviou, também tem SHA-256 registrado.
- O registro completo, com os comandos, está em `som/preservado_r13/preservado_r13.json`.
- **Arquivo de escuta (160 MB):** não está no git. É recriado pelo comando registrado, a partir das partes do R12 e do FLAC da B.

## 6. Licenças

- **Narração:** plano gratuito da ElevenLabs, **sem uso comercial** e com atribuição obrigatória.
- **Música:** Pixabay Content License; a conferência da página fica com você.
- **Efeitos:** Freesound CC0 e Mixkit Sound Effects Free License, ambos sem atribuição. Detalhes em `relatorios/licencas_r13.md`.

**Nada foi publicado.** O definitivo R13 só será produzido depois da sua aprovação.
