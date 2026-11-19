# Ep. 01 · Buzina de navio na abertura e na conclusão (para aprovação)

**Comparativo:** `episodio/ep01_comparativo_buzina.mp4` (32 s).
- **Abertura** (3,4–11,4 s) e **conclusão** (160–168 s), cada uma primeiro **SEM** e depois **COM** buzina.
- Mesma imagem (revisão aprovada) e mesma narração no **mesmo nível** nas duas versões: −13,31 LUFS na abertura, −12,66 LUFS na conclusão.
- Base: a direção sonora refinada, com reduções de água e efeitos interativos intactos. A versão sem buzina continua idêntica byte a byte; a com buzina só acrescenta os dois toques.

**Escopo:**
- A buzina **ainda não foi incorporada** à versão refinada completa: isso acontece depois da sua aprovação.
- Nenhuma animação foi alterada.
- Nada foi publicado e o render de 1080 × 1920 não foi iniciado.

> ⚠️ A narração segue sob a pendência de licença do plano gratuito da ElevenLabs. O episódio **não está licenciado para exploração comercial** (`voz/LICENCA_NARRACAO.md`).

## Gravação

- **Arquivo:** "Cruise ship Albatros ship horn" — Tvabutzku1234, Wikimedia Commons, **CC0 (domínio público)**.
  - Página: https://commons.wikimedia.org/wiki/File:Cruise_ship_Albatros_ship_horn.ogg
  - Uso comercial permitido; atribuição não exigida, mas registrada em `som/fontes_efeitos_refinado_buzina.md` e nos créditos.
- **O que é:** gravação **real** de um navio de cruzeiro despedindo-se do porto de Bremerhaven com três toques.
- **Por que esta:**
  - O Mixkit não tem buzina de navio, só de carro, trem ou efeitos de trailer.
  - No Commons, as outras opções eram apitos de locomotiva (timbre errado) ou "Costa Favolosa horn", que é CC BY-SA, licença que temos evitado.
  - Não há gravação livre e verificável de um cargueiro específico. A buzina de um navio grande tem o mesmo tipo de som (tifão grave).
- **Análise objetiva:**
  - Fundamental ~115 Hz, com harmônico forte em ~231 Hz, dentro da faixa das embarcações acima de 200 m.
  - Gravação mono, portanto segura em mono e no celular.
  - Antes e depois dos toques, o fundo é quase todo abaixo de 80 Hz (vento no microfone): removido com filtro passa-alta em 80 Hz.
  - Entre os toques há o eco real no porto.
  - Quase não há energia em 2–8 kHz fora da buzina, então não vejo sinal de vozes próximas. É uma checagem limitada: o detector de fala Whisper segue indisponível nesta sessão.

## Como o toque foi construído (só com a gravação real)

1. **Ataque natural:** o fim da subida de pressão do 1º toque, ~0,5 s. O ataque completo da gravação leva ~1,3 s e deixava a buzina sem presença no momento certo.
2. **Sustentação breve:** um trecho estável. 1,0 s na abertura, 0,7 s na conclusão. Os toques originais têm 7–8 s.
3. **Dissipação progressiva:** o fim real do último toque, com o corte do sopro e o eco do porto.
4. **Ligações:** fusões de 0,25 s entre as partes.
5. **Escala:** levemente mais grave (−1,8 semitom, ~104 Hz) para soar como um cargueiro. **É uma alteração da gravação original, aplicada nos dois toques para manter a identidade.** Se preferir o tom original, é só desfazer.
6. **Mesmo timbre nos dois momentos:** a mesma construção, a mesma gravação e o mesmo tom.

## Posicionamento e equilíbrio

| | Abertura | Conclusão |
|---|---|---|
| Início | 5,85 s: o ataque cai na pausa depois de "Mas olha este gigante:" | 165,6 s: nasce sob "navio." (a última palavra termina em 166,12 s) |
| Perspectiva | <ul><li>Distância real câmera → navio: no aéreo (~390 m) é mais suave e menos aguda.</li><li>No corte para o plano próximo (6,4 s) fica mais presente.</li></ul> | <ul><li>Distância real do plano final, mais filtrada (mais longe e mais discreta).</li><li>Mais reverberação de mar aberto.</li></ul> |
| Duração audível | ~4,2 s (até ~10 s) | ~1,9 s: o fade natural do encerramento a dissolve **até 168,0 s**, sem prolongar o vídeo |
| Pico (fones) | −23,8 LUFS | −32,1 LUFS |
| Em relação ao resto do som | **+8,2 dB** acima de efeitos, ambiências e trilha: destaca-se | **+1,5 dB** acima: integrada à trilha e ao mar, discreta |
| Em relação à narração | **15 dB abaixo** da voz quando há fala; ocupa a pausa sem competir | depois da última palavra, sem sobrepor a voz |
| Celular (350 Hz–7 kHz, mono) | audível pelos harmônicos: +8,6 dB sobre o resto, 26,6 dB abaixo da voz | +6,2 dB sobre o resto |
| Mono | igual aos fones (gravação mono) | igual |

**Encerramento:**
- A buzina soa sobre o acorde final da trilha.
- O fim continua natural, sem vinheta, mascote ou assinatura.
- Duração do episódio: 168,0 s.

## Mixagem com buzina (verificação)

| | Refinado sem buzina | **Com buzina** |
|---|---|---|
| Loudness integrado | −14,03 LUFS | **−14,03 LUFS** |
| Pico verdadeiro (WAV) | −1,8 dBTP | **−1,8 dBTP** |
| Mono | −14,04 LUFS | **−14,04 LUFS** |
| Voz no celular: fala ≥ 10 dB acima do fundo | 97,2% | **97,1%** |
| Narração e trilha | — | mesmos níveis: a buzina não foi compensada baixando narração nem trilha |
| Outros sons | — | idênticos à versão refinada |

**Limite:** são medições. Não escuto o resultado; a decisão sobre timbre e presença da buzina é da sua escuta.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `som/som_refinado.py` | função `buzina()`; ativada com `BUZINA=1`, níveis em `BUZINA_DB` (atual: −5 dB na abertura, −19 dB na conclusão) |
| `audio_ep01_refinado_buzina.wav` + stems `*_refinado_buzina.wav` | mix e stems (fora do git) |
| `stems/categorias/ep01_efeitos_buzina_refinado_buzina.wav` | buzina isolada (fora do git) |
| `som/medidas_buzina.json` | medidas da buzina |
| `som/buzina_reproducao.json` | fones, celular e mono |
| `som/comparativo_buzina_medidas.json` | níveis dos trechos do comparativo |

## Depois da aprovação

1. Incorporar as buzinas à versão refinada completa.
2. Montar os 168 s pelo master de imagem (`trocar_audio.py`, sem render 3D).
3. Render de 1080 × 1920 só com autorização.
