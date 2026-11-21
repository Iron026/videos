# Ep. 02 · Narração APROVADA — validação

**Arquivo recebido em 21/11/2026:** `ElevenLabs_2026-11-21T21_13_42_Will_-_Deep_pvc_s60_sim75_v4.mp3` (somente leitura)
SHA-256 `fdedd87772aee9d4dac5d0193db3b9e1ef97c4b699c8ce01b0c8de7ae05726ee`, idêntico ao arquivo enviado.

| Item | Resultado |
|---|---|
| Formato | MP3, 44,1 kHz, mono, 129 kb/s |
| Duração | **149,89 s** (fala de 0,11 a 149,64 s) |
| Loudness original | −21,7 LUFS · pico −1,7 dBFS (o Ep. 01 tinha −21,9 LUFS / −1,8 dBFS) |
| Ritmo | 384 palavras em 149,5 s = **154 palavras/min** (o Ep. 01 tinha 135,6). A voz está ~10 % mais rápida |

## Conteúdo × roteiro — o que foi e o que NÃO foi verificado

- **Não verificado palavra por palavra.** O modelo Whisper local não pôde ser baixado nesta sessão: o acesso à rede foi
  liberado no ambiente, mas o download foi negado pela política de permissões. Nada foi transcrito por serviço externo e
  nenhum crédito da ElevenLabs foi usado.
- **Verificação estrutural (alinhamento por pausas, `alinhar_por_pausas.py`):**
  - os **37 fins de frase** do roteiro caem em pausas do áudio, todos em ordem;
  - 66 das 67 fronteiras de pontuação casam com pausas; resíduo médio de 0,43 s em relação ao ritmo esperado (máximo 1,28 s);
  - há 11 pausas extras, todas em pontos naturais de ênfase ("o ‖ fluido refrigerante", "não ‖ cria frio", "e ‖ quente por fora");
  - **nenhum sinal** de frase ausente, repetida ou fora de ordem, nem de tag de voz ("[curiously]" etc.) lida em voz alta.
- Os tempos por palavra (`roteiro/palavras_pausas.json`) são **aproximados dentro das frases**; os tempos de frase são
  confiáveis. Eles já guiam o animatic (selo "narração não verificada").

## Aprovação
**Aprovada pelo usuário em 21/11/2026** ("essa é a narração aprovada"). O texto enviado junto é idêntico, caractere a
caractere, ao `roteiro/roteiro_oficial.md` (SHA-256 em `roteiro/roteiro.sha256`). Os tempos estão em `roteiro/palavras.json`
(alinhamento por pausas; metadados em `roteiro/palavras_meta.json`).

## Pendências
1. **Verificação palavra a palavra** (Whisper local), que depende da autorização do download do modelo.
2. **Licença:** o nome do arquivo segue o padrão do Ep. 01 (plano gratuito: uso não comercial, atribuição obrigatória).
   O plano usado nesta geração precisa ser confirmado.
3. **Duração:** com esta narração o episódio tem ~151 s (2min31s), abaixo da faixa pretendida de 2min40s–2min55s.
   Pelo pedido, a duração segue a narração aprovada; nada foi esticado.
