# Episódio 01 · Animatic r2 (revisão de direção)

**Arquivo:** `animatic/animatic_ep01_r2.mp4` · 1080×1920 · 30 fps · H.264 + AAC 48 kHz
**Versão anterior preservada:** `animatic/animatic_ep01.mp4` (v1, 19,5 s).
**Status da narração:** **definitiva pendente.** As legendas são provisórias, com tempos estimados (~145 palavras/min, ritmo medido da amostra), e **não** são a sincronia definitiva. A única voz é a amostra Will - Deep que você gerou, na assinatura.

## O que mudou

| | v1 | r2 |
|---|---|---|
| Animação principal | 14,80 s | **13,75 s** |
| Assinatura | 4,70 s | **3,10 s** (voz entra 0,45 s antes, em J-cut) |
| Total | 19,50 s | **16,85 s** |
| Queda do bloco | câmera a ~24 m, lente 40 mm, tempo real | câmera a ~8 m, na linha d'água; **câmera lenta 0,35×** na entrada na água; tranco de câmera no impacto; recuo final revela o bloco no fundo |
| Aproximação aérea | 6,25 s | **2,40 s**, acelerando, com **corte em movimento** |
| Içamento | dentro da aérea (chapa pequena no quadro) | **plano novo (3a, 3,25 s):** contra-plongée, a chapa entra pelo alto do quadro e desce |
| Encaixe | close aprovado | o mesmo close (3b), agora com 3,50 s |
| Transições | 2 fusões | fusão cais→estaleiro (0,2 s), cortes secos 7,00 s e 10,25 s, fusão curta para a assinatura |

## O que foi preservado (sem reconstruir a cena)

- **Cenas, modelos, física e movimento do pórtico:** são as mesmas funções da v1 (`animatic.py`). A r2 (`animatic_r2.py`) só troca as câmeras e o mapeamento do tempo. Conferi que a exportação da v1 continua idêntica byte a byte.
- **Movimento do guindaste:** mesma trajetória. Só a descida longa foi levemente comprimida (5,9 s → 5,65 s, fator 1,04). A descida final (1,0 s) e o deslize para dentro do vão (1,9 s) seguem em **tempo real**, então o balanço do pêndulo (calculado da aceleração) e o **limite de folga que corrigiu a colisão com as cavernas** valem sem nenhuma alteração.
- **Física da queda:** mesma integração (empuxo, massa adicional, arrasto). A câmera lenta muda só o tempo de apresentação: a água, as bolhas e os respingos seguem o tempo de cena, exportado por quadro.

## Assinatura de 3 segundos: viável, com dois cuidados

A frase completa dura 3,30 s de fala na amostra (1,50 s + pausa de 0,455 s + 1,80 s). Em 3 s de tela, sem acelerar a voz de forma perceptível, foi possível assim:

1. **Pausa encurtada** de 0,455 s para 0,22 s, com o corte feito no silêncio.
2. **+5% de velocidade** (atempo 1,05, altura preservada). Abaixo do limiar em que a aceleração costuma ser percebida.
3. **J-cut:** "De Olho…" começa 0,45 s antes da tela da assinatura, sobre o encaixe já concluído. Com isso a assinatura ocupa 3,10 s.

Tudo isso foi feito numa cópia derivada (`voz/amostra_assinatura/narracao_assinatura_r2.wav`). **O MP3 original não foi tocado** (SHA-256 d21f3e15… conferido).

**Alternativa, se preferir a assinatura isolada sem J-cut:** 3,5 s com a mesma edição, ou 2,0 s só com "De Olho no Invisível" falado e o slogan apenas escrito. Esta segunda opção muda a frase, então não a apliquei.

## Linha do tempo r2

| Tempo (s) | Plano | Legenda provisória |
|---|---|---|
| 0,00–4,80 | 1 · Cais: empurrão 0,50 · água 2,65 (câmera lenta 0,35× de 2,1 a 3,6 s, com rampas) · leito 4,01 | "Se eu jogar este bloco / de aço na água, / ele afunda." |
| 4,60–7,00 | 2 · Aérea curta (fusão 4,60–4,80) | "Mas e se eu usar toneladas" |
| 7,00–10,25 | 3a · Içamento: a chapa desce para o quadro | "do mesmo aço para construir / um navio?" |
| 10,25–13,75 | 3b · Close aprovado: descida final, deslize, encaixe em 13,15 | "Parece impossível." / "Então vamos montar um." |
| 13,30 | voz real (J-cut) | |
| 13,75–16,85 | 4 · Assinatura curta | (voz) |

## Validação técnica (`animatic/validacao_animatic_r2.json`)

| Verificação | Resultado |
|---|---|
| Vídeo | H.264, 1080×1920, 30 fps, 505 quadros, 16,83 s |
| Quadros pretos / congelamentos ≥ 1 s | nenhum / nenhum |
| Loudness integrado · pico real | −14,0 LUFS · −1,7 dBTP |
| Posição da voz (correlação com a cópia editada) | 13,303 s, prevista 13,30 s (+3 ms) |
| Transcrição da voz no MP4 (Whisper) | "De olho no invisível, o invisível ganha a forma." Frase inteira reconhecida mesmo com a pausa encurtada e +5% de velocidade |
| Custo de render | plano 1: 145 quadros a 7,4 s/quadro · planos 2/3: 275 quadros a 10,1 s/quadro (≈ 64 min no total, sem GPU) |

Comparativo visual: `animatic/comparativo_r2.jpg`. Folha de contato: `animatic/folha_contato_r2.jpg`.

## Limitações

1. Legendas e tempos são estimativas. Tudo será refeito sobre a narração definitiva, que ainda não existe.
2. A câmera lenta usa o mesmo shader de água. Não há simulação de fluido real, e o respingo continua discreto.
3. O "a" extra em "ganha **a** forma" da amostra continua lá (ponto já apontado na análise da voz).
4. Nada foi publicado e o episódio completo não foi renderizado. Não rodei benchmarks novos.
