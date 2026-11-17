# Episódio 01 · Animatic (avaliação)

**Arquivo:** `animatic/animatic_ep01.mp4` · 1080×1920 · 30 fps · 19,5 s · H.264 + AAC 48 kHz
**Motor:** Three.js v2 (GTAO 8 amostras, MSAA 4×), cenas modeladas no Blender 5.1 e exportadas por código.
**Status da narração:** **definitiva pendente.** Nos planos 1–3 o texto do roteiro aparece só como legenda. A única voz no áudio é a amostra real que você gerou no site da ElevenLabs (Will - Deep, plano gratuito, só para avaliação), colocada na assinatura.

## Linha do tempo

| Tempo (s) | Plano | O que acontece | Legenda (narração provisória) |
|---|---|---|---|
| 0,00–5,60 | 1 · Cais | Bloco de aço de 1,6 m empurrado (1,40 s), cai do cais (2,30 s), entra na água (3,13 s), toca o leito (3,76 s); bolhas e respingos | "Se eu jogar este bloco / de aço na água, / ele afunda." |
| 5,25–5,60 | fusão | | |
| 5,25–11,50 | 2 · Estaleiro | Vista aérea → aproximação ao enquadramento aprovado do Quadro 2; o pórtico desce o painel por fora do casco | "Mas e se eu usar toneladas / do mesmo aço para construir / um navio?" |
| 11,50–15,15 | 3 · Vão do costado | Close: painel termina a descida, o carro o leva para dentro do vão, encaixe em 14,40 s (impacto metálico) | "Parece impossível." / "Então vamos montar um." |
| 14,80–15,15 | fusão | | |
| 14,80–19,53 | 4 · Assinatura | Mascote oficial 2D, título, slogan, @deolhonoinvisivel; carrilhão em 14,95 s | Amostra real "De Olho no Invisível… O invisível ganha forma." a partir de 15,20 s |

## Física usada (por que o movimento é crível)

- **Queda do bloco:** aço 7.850 kg/m³, empuxo, massa adicional 0,5 e arrasto Cd 1,05 integrados quadro a quadro. Ele desacelera ao entrar na água e chega ao leito 0,63 s depois, sem flutuar.
- **Içamento do painel:** como no estaleiro real, a chapa desce **por fora** do casco com folga de 2,2 m (a folga mínima calculada com a forma do costado perto da proa é 1,9 m) e só então o carro do pórtico a desliza para o vão.
- **Balanço da carga:** pêndulo ≈ −a/g, limitado a ±2° pelos cabos-guia. Correção desta rodada: na frenagem, a base da chapa balança em direção ao casco; o giro agora é limitado também à folga que ainda resta. Antes, nos últimos centímetros, a borda inferior atravessava as cavernas (quadros 13,98–14,25 s); verifiquei que não era erro do renderizador (sem MSAA, sem GTAO, mesma posição de vértices no Blender e no Three.js).
- **Cabos:** comprimento recalculado a cada quadro conforme o moitão sobe ou desce.

## Áudio

- Efeitos originais sintetizados em código e sincronizados com os eventos da simulação: raspagem no concreto, impacto e respingos (3,13 s), ambiente subaquático e bolhas, baque no leito (3,76 s), whooshes nas fusões, ambiente do estaleiro, motor do pórtico, impacto metálico do encaixe (14,40 s) e carrilhão da marca (14,95 s).
- Voz: somente a amostra real, normalizada a −16 LUFS pelo `voz/preparar_narracao.py`, com ducking dos efeitos durante a fala.
- Master: −14 LUFS integrado / −1,5 dBTP (padrão de plataformas de vídeo curto), em duas passagens de `loudnorm`.

## Validação técnica

Ver `animatic/validacao_animatic.json` (gerado por `validar_animatic.py`).

{{VALIDACAO}}

## Duração

O animatic tem 19,5 s, acima dos 10–15 s previstos inicialmente para este trecho. A diferença vem do texto aprovado do roteiro no ritmo medido da amostra (~140 palavras/min) e dos 4,7 s da assinatura com a frase completa. Quando houver a narração definitiva, os tempos dos planos serão reajustados às palavras reais (o `preparar_narracao.py` já gera `palavras.json` com os tempos de cada palavra).

## Custo de render

- Plano 1: 169 quadros · plano 2/3: 298 quadros · assinatura: 142 quadros (HTML/SVG).
- Three.js v2, sem GPU: cerca de 8–12 s por quadro em 1080×1920, ou ≈ 1 h 20 min para os 467 quadros 3D.

## Limitações conhecidas

1. **Narração:** os tempos das legendas são estimados. A voz definitiva (licença comercial da ElevenLabs) ainda não existe, e o conector não foi usado.
2. **Amostra:** possível "a" extra em "ganha a forma" (40 ms, confiança 0,70 do reconhecimento). Precisa ser ouvida por você antes de virar referência.
3. **Água no plano 1:** as ondas de impacto são procedurais no shader. Não há simulação de fluido real nem espuma persistente.
4. **Plano 2:** a aproximação aérea é rápida (6,25 s); talvez precise de mais tempo quando a narração real chegar.
5. **Personagens:** o mascote aparece só como a imagem 2D oficial na assinatura; a modelagem 3D continua suspensa.
6. **Nada foi publicado** e o episódio completo não foi renderizado.
