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

## Verificação palavra a palavra (rodada 2, 22/11/2026)
- **Modelo:** `openai/whisper-large-v3`, pesos oficiais publicados pela OpenAI (licença MIT), baixados sem credenciais e
  convertidos localmente para CTranslate2. A transcrição rodou **100 % local**, com o Hugging Face em modo offline: o áudio
  não saiu da máquina. O MP3 não foi alterado (SHA-256 conferido no relatório).
- **Resultado:** **384 de 384 palavras do roteiro reconhecidas, na ordem**, com confiança média de 0,99. Nenhuma palavra
  falta, sobra, foi trocada ou está fora de ordem.
- **Única divergência:** o Whisper registrou "condensador. Veja o" a 116,52 s, com **duração zero**. Retranscrito sem
  contexto, o trecho diz exatamente "Agora pense no que acontece quando você deixa a porta aberta". Era um artefato do
  decodificador, não fala.
- **Tempos** (`refinar_tempos.py`):
  - a identidade das palavras vem do Whisper;
  - o instante de início depois de cada pausa vem do ataque acústico medido, porque o Whisper põe esses inícios ~0,3 s
    dentro do silêncio;
  - as 78 pausas detectadas foram todas atribuídas;
  - o fim da fala é o medido no sinal (149,64 s).
- **Erros da v1 encontrados:**
  - E3 entrava 1,87 s cedo, E4 2,57 s cedo e H1 1,48 s cedo;
  - A2 e A3 entravam ~1 s tarde;
  - dentro das frases, as palavras da v1 estavam em média 0,29 s fora do lugar (até 2,6 s em E2/E3).
- **Cortes:** os outros 34 dos 39 cortes caem **exatamente** no mesmo instante da v1.
- **Limite:** eu meço, não escuto. Pronúncia, entonação e naturalidade não foram avaliadas por mim.

## Pendências
1. **Licença:** o plano da ElevenLabs usado nesta geração **não foi informado**. Até a confirmação, a narração fica tratada
   como plano gratuito (sem uso comercial, atribuição obrigatória), como a do Ep. 01.
2. **Duração:** 151,24 s, aprovada pelo usuário. Nada foi esticado.
