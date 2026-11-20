# Ep. 01 · Teste curto em resolução definitiva (1080 × 1920)

## Entregas

| Entrega | Arquivo |
|---|---|
| Trechos de teste em 1080 × 1920, 30 fps, com rótulos, legendas, narração, mixagem refinada e buzinas (9 s) | `episodio/ep01_teste_1080_trechos.mp4` |
| Comparativo lado a lado: aprovado 540 × 960 (ampliado) × teste 1080 (9 s) | `episodio/ep01_comparativo_1080_x_aprovado.mp4` |
| Janelas da superestrutura: aprovado × teste × correção proposta | `episodio/ep01_teste_1080_janelas.jpg` |
| Números | `validacao_teste_final.json` |

**Trechos testados:**
- experimento 87–90 s (s08b);
- avaria 140–143 s (jato, espuma, nível subindo);
- avaria 146–149 s (divisórias, superestrutura ao fundo).

**Qualidade:** a mesma da revisão aprovada (oclusão ambiente de 16 amostras, antisserrilhado 4×, bloom 0,22, correção de cor), só que em `escala=1`.

O áudio é a mixagem aprovada (`audio_ep01_refinado_buzina.wav`), e a narração original não foi alterada.

> Não consigo assistir como você. Os resultados vêm de métricas e da inspeção de quadros e recortes ampliados.

## Resultado: **nenhuma regressão**

| Verificação | Experimento 87–90 s | Avaria 140–143 s | Avaria 146–149 s |
|---|---|---|---|
| Fidelidade ao aprovado: SSIM do quadro 3D reduzido a 540 × 960 | 0,987 | 0,986 | 0,974 (mín. 0,958 em 147,0 s: janelas, ver abaixo) |
| Fidelidade ao aprovado: SSIM do quadro composto | 0,976 | 0,961 | 0,956 |
| Pontos isolados por megapixel (1080 × aprovado) | 2.436 × 6.107 | 1.559 × 3.241 | 5.359 × 7.988 |
| Cintilação média, 1080 reduzido × aprovado | 6,73 × 6,88 | 4,11 × 4,24 | 4,69 × 5,10 |
| Piscadas locais que só existem em 1080 | 0 | 0 | 2 quadros (148,27–148,30 s: janelas, ver abaixo) |
| Áudio: nível e diferença contra o aprovado | igual (±0,01 dB) · −39 dB (só recodificação) | igual · −43 dB | igual · −42 dB |

A queda do SSIM no quadro composto em relação ao 3D é esperada: legendas e rótulos são desenhados com o dobro de nitidez em 1080.

- **Vazamento do mar (correção de profundidade):**
  - funciona em 1080;
  - no pico do experimento (88,85 s), o oclusor antigo deixaria 9.070 pixels de mar vazando; com a correção, a área fica igual à cena sem mar (diferença 2,6, contra 27,2 com o oclusor antigo);
  - na avaria, o mesmo resultado.
- **Água, transparência, jato, espuma, linha d'água:** sem artefatos. Mesma aparência do aprovado, com bordas mais limpas.
- **Sombras e oclusão ambiente:** sem acne, sem serrilhado, sem cintilação. O mapa de sombras (4096) se mantém adequado em 1080.
- **Materiais e iluminação:** iguais aos aprovados.
- **Determinismo:**
  - os mesmos quadros renderizados isoladamente e no lote paralelo ficaram iguais (diferença média 0,04–0,15 de 255);
  - a falha vista antes nos lotes paralelos em 540 não se repetiu.

## Defeito já existente: janelas da superestrutura (não é regressão)

**O defeito:**
- Quando a câmera passa rente à superestrutura (avaria, ~146,5–148,3 s), a faixa de janelas aparece **pontilhada e trêmula** em vez de vidro escuro.
- Está **igual na revisão aprovada** em 540 × 960. Em 1080, o padrão só fica mais fino.
- É a causa da queda de SSIM em 147,0 s e das 2 "piscadas" em 148,27 s.

**Causa, testada:**
- **Conflito de profundidade (z-fighting):** a faixa de janelas fica só 6 cm à frente da parede.
- Desligar sombras ou oclusão ambiente não muda nada; ocultar as janelas faz o padrão sumir.

**Correção proposta, não aplicada:**
- Uma pequena prioridade de profundidade (*polygon offset*) só no material das janelas (`janoff=1` no renderizador).
- No plano afetado, as janelas viram faixas sólidas de vidro escuro, como foram modeladas.
- Em navegação, porto e plano final, onde as janelas já aparecem corretas, a mudança é imperceptível (só ruído de borda).
- Um offset maior (4) já criaria bordas indevidas, então o valor 1 é o indicado.
- O parâmetro foi deixado **desligado por padrão**, para não mudar nada do que foi aprovado sem a sua decisão.

## Para decidir antes do render completo

1. **Janelas:** incluir `janoff=1` no render definitivo? É recomendado: corrige um defeito concreto e é neutro nos outros planos.
2. **Selo "VERSÃO DE REVISÃO · não publicar":** hoje a montagem o desenha também no perfil `final`. Antes do render definitivo, ele precisa ser retirado, ou mantido se o arquivo ainda for de revisão.
3. **Configuração do render:**
   - o script antigo `render_segmentos.sh final` usa uma qualidade desatualizada (AO 8, sem bloom);
   - o render definitivo deve usar `escala=1&aoamostras=16&msaa=4&bloom=0.22` (como este teste), mais `janoff=1` se aprovado;
   - os 270 quadros deste teste já estão em `quadros_final/` com essa configuração e podem ser reaproveitados, exceto os afetados pelas janelas, se `janoff=1` for aprovado.
4. **Tempo estimado:**
   - em um processo, ~3,9 s por quadro: **~5,5 h para os 5.040 quadros**;
   - três processos em paralelo ficaram mais lentos no total (~14–15 s por quadro cada) e, em 540, já tinham produzido uma falha não determinística;
   - por isso, o recomendado é um processo por vez, com verificação de quadros ao final.

## O que não foi feito

- Nenhum ajuste estético; nenhuma mudança de narração, mixagem, buzinas, legendas, física ou duração.
- O render completo de 168 s não foi iniciado.
- Nada publicado.
- A narração segue do plano gratuito da ElevenLabs: o episódio **não está licenciado para exploração comercial** (`voz/LICENCA_NARRACAO.md`).
