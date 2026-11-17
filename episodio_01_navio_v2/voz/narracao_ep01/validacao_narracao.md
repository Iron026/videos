# Validação da narração · Episódio 01

**Original preservado:** `voz/narracao_ep01/Narração ep 1.mp3` (somente leitura)
SHA-256 `79e1e8f21f30c4d00a5ec4fd4e6443b734e41ac249cdd5b170a99c7224949ba0`, idêntico ao arquivo recebido.

## Integridade

| Item | Resultado |
|---|---|
| Formato | MP3, 44,1 kHz, mono, 128 kb/s (codificador Lavf 63) |
| Duração | **170,344 s** (confere com os ~170,34 s informados) |
| Decodificação completa | sem erros |
| Loudness original | −21,9 LUFS, LRA 3,4 LU, pico −1,8 dBFS |
| Fala | da primeira palavra em 0,00 s à última em 169,86 s; maior pausa entre frases 0,64 s |
| Ritmo | 135,6 palavras/min |

**Cópia de trabalho:** `trabalho/narracao_48k.wav` (48 kHz, mono, 24 bits, −16 LUFS). A velocidade da voz não foi alterada.

## Conteúdo × roteiro (384 palavras)

- O roteiro oficial está salvo em `roteiro_ep01.txt` e tem exatamente **384 palavras**.
- Transcrição automática (Whisper small, local) comparada palavra a palavra: **WER 2,3%**.
- **Nenhuma frase ausente, repetida ou fora de ordem.** As 49 frases do roteiro aparecem na sequência certa (tempos em `trabalho/frases.json`; tempos por palavra em `trabalho/palavras.json`).

As diferenças apontadas pela transcrição, uma a uma:

| Trecho (s) | Roteiro | Transcrição | Avaliação |
|---|---|---|---|
| 31,98 | "detalhe importante" | "detalhe -os importante" (20–40 ms, confiança 0,33) | Provável transição entre palavras, não uma sílaba extra. **Ouvir** `pontos_escuta/01` |
| 63,4 | "Arquimedes" | "Archimedes" / "Arquimédios" (0,76) | Grafia do reconhecedor. A palavra dura 0,7 s, com 4–5 núcleos silábicos. **Confirmar a pronúncia** `02` |
| 99,2 | "contêineres" | "containers" (0,49) | Viés do reconhecedor para a grafia inglesa; a energia mostra ~4 sílabas. **Confirmar** `03` |
| 118,5 | "profundidade, medida" | "profundidade e medida" (0,31) | A "palavra" ocupa a pausa da vírgula (0,40 s). Provável respiração. **Ouvir** `04` |
| 119,3 | "da quilha" | "daquilha" | Só junção na escrita, sem diferença de fala |
| 152,2 | "divisórias estanques" | "divisória as estanques" (0,35) | Ligação natural do "s" com o "e" seguinte (pronúncia correta) `05` |
| 169,4 | "ganha forma" | "ganha **a** forma" (40 ms, 0,75) | O mesmo ponto já visto na amostra anterior. Pode ser um "a" prolongado ou um "a" inserido. **Ouvir** `06` |

Também conferi as palavras pedidas:

| Palavra | Tempos (s) | Confiança |
|---|---|---|
| empuxo | 62,16 · 66,60 · 71,16 · 113,68 | 0,82–1,00 |
| calado | 122,70 · 127,02 | 0,90–0,95 |
| assinatura | 166,56–169,86 | "De Olho no Invisível." completo |

**Conclusão:** não encontrei erro relevante que impeça a produção. Seis pontos dependem de escuta humana (trechos de 2 a 4 s em `pontos_escuta/`). O principal é o "ganha (a) forma" da assinatura oficial. Se houver erro, só a assinatura e a legenda correspondente precisariam de ajuste.
