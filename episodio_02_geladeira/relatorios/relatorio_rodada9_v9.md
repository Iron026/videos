# Ep. 02 — Rodada 9: V9 completa em 540 × 960

**Arquivo para assistir:** `episodio/ep02_v9_revisao.mp4` (SHA-256 `c4e646f0…`).
- 4.537 quadros, 30 fps, 151,233 s. Mesma contagem, cadência e duração da V8 e da V9a.
- Decodifica inteiro sem erro.

**Estado das versões:**
- **Nada publicado.** Nenhuma voz gerada, nenhum serviço contratado, Episódio 01 intacto.
- **Render definitivo em 1080: não iniciado.**
- **V8 e V9a preservadas:** hashes conferidos em `relatorios/versoes_preservadas_r9.json`.
  - O `montar_ep02.py` da V9a é recuperável no commit `a931e79`; ele foi editado depois, ganhando novas opções.
  - Com as opções novas desligadas, o código reproduz a V8.

Eu meço, mas não assisto nem escuto como uma pessoa. A naturalidade dos movimentos e do som é avaliação sua.

## Arquivos

| Arquivo | O que mostra |
|---|---|
| `episodio/ep02_v9_revisao.mp4` | a V9 completa, com som |
| `episodio/comparativos_v9/*.mp4` | **V9a × V9 lado a lado**, com o som da V9: `a1_a2_abertura`, `a3_a4_corte_seco`, `c3_c4_d1_aproximacao`, `d3_pote_vermelho`, `h2_corte_itens`, `i1_i2_leite_saida`, `j1_j3_sem_leite` |
| `episodio/comparativos_v9/c4_obturador_teste_real_e_4x_lento.mp4` | fim do C4: V9 × obturador de 180° (teste, **desligado**) |
| `relatorios/comparativos_r9/v9a_x_v9_quadros.jpg` | 12 instantes, V9a em cima e V9 embaixo |
| `relatorios/comparativos_r9/c4_ultimo_x_d1_primeiro_v9.jpg` | último quadro do C4 × primeiro do D1 |
| `relatorios/comparativos_r9/c4_q151_v9_x_obturador.jpg` | C4 q151: V9 × obturador |

## 1. O que mudou (só o que você aprovou)

| Decisão | Como está na V9 |
|---|---|
| A3 → A4 | **corte seco em 4,87 s**: sem imagem fantasma da serpentina sobre o rosto. Atuação e tempos iguais |
| A1/A2 | personagem 15 cm mais perto do puxador; solta a ~20° e recua para fora do giro da porta; mão esquerda no batente. Câmera igual |
| I1/I2 | pega em ≈ 118,44 s, retirada, saída, câmera volta para a geladeira; contato mão × caixa constante; leite ausente do I2 ao I4 e no J1–J3. Duração igual |
| D3 | pote vermelho no centro, sem reenquadrar; o feixe de calor sai dele |
| Itens | pote de sorvete retirado; os demais como na prévia |
| C4 → D1 | aproximação ao evaporador (E4 → F1 não mudou) |
| Porta | folga de 0,5 mm mantida (sem sobreposição, sem 0,15 mm) |
| Áudio | só os passos novos do I1; **sem** o teto de −2,0 dB |
| Composição | a da V9a, aprovada |

## 2. Correção que eu fiz durante o render (regressão minha, já corrigida)

**Porta no corte A1 → A2:**
- **Defeito:** a curva física da porta da rodada 9 valia só no A1. No corte de 1,35 s a porta saltava de 88,5°, ainda
  em movimento, para 100° parada no A2. Na V8 os dois planos tinham 100° e não havia salto.
- **Correção:** o A2 agora segue a mesma curva do A1. Só a animação da porta mudou: malhas, materiais, câmera,
  personagem e rótulos estão iguais, conferidos sem considerar a ordem dos triângulos.
- **Movimento resultante:** 86,9° → 89,3° no corte, com a velocidade contínua (49,5 → 46,7 °/s), até parar em 100° em
  1,87 s. O mesmo vale para o I1 → I2, que para em 100° no corte.
- **Aceleração:** **nenhuma** depois do pico, nos dois casos (`relatorios/porta_v9_perfil.json`). A porta só desacelera
  depois da soltura; não parece abrir sozinha.
- **Colisões:** braço × porta ≥ 436 mm durante todo o A2. Depois da soltura, ≥ 11,9 mm no primeiro quadro e ≥ 102 mm a
  partir de 0,6 s.
- **Quadros antigos do A2:** guardados em `quadros_revisao/A2/_descartados/`; a cena antiga, em
  `cenas_descartadas_r9/`.

## 3. Render em 540: como foi feito e provado

**O que foi re-renderizado:**
- **31 planos, 4.045 quadros**, um processo por vez, com manifesto por quadro (SHA-256, gravação atômica, retomada).
- **11 planos reaproveitados da V8 com prova** (geometria ou oclusão): A3, D2, D4, E1, E2, E3, E4, F1, F2, G3z, J4.
  - Número de quadros = cena atual; prova registrada com o hash da cena atual.

**Paradas do verificador:** o verificador parou 4 vezes por "salto" entre quadros. Investiguei cada caso antes de
retomar; nenhum era defeito.

| Parada | Causa | Prova |
|---|---|---|
| A2 q18 | varredura da visão térmica (efeito da cena) | a V8 tem o mesmo salto (0,917) |
| C1 q16–27 | porta fechando depressa | V8 com o mesmo salto (±0,002); quadro novo × V8 ≥ 0,998 |
| C4 q148–153 | aproximação aprovada (~20 mm/quadro) | prévia aprovada com o mesmo salto; novo × prévia = 1,000 |
| I1 q102–103 | câmera volta enquanto o personagem sai | mesmo perfil da prévia (±0,01); difere só no ângulo da porta (curva corrigida depois da prévia) |

**Como os saltos passaram a ser aceitos:**
- O verificador só aceita um salto quando há **prova**: efeito da cena mudando naquele quadro, ou o mesmo salto numa
  versão aprovada com a imagem equivalente (≥ 0,93).
- A outra via é um registro **investigado** com evidência: `relatorios/saltos_investigados_r9.json`.
- Cada aceite fica no log e no manifesto do quadro. Fora disso, o verificador continua parando.

## 4. Testes (antes e depois da montagem)

| Teste | Resultado |
|---|---|
| Colisões e continuidade (`testar_itens`, `testar_leite`, `testar_a1`) | sem invasões novas; mão × caixa −3,1 mm (segurando), caixa ≥ 0,5 mm do vidro; alcance do puxador ≤ 3,3 mm durante a pega; braço × porta: acima |
| Leite ausente no J1–J3 | conferido na V9 montada (folha de quadros) |
| Porta × vedação (C4 G3 H1 H2 J3), V9 × V8 nos mesmos quadros | C4: 11.448 × 12.522 px; G3: 15 × 15; H1: 10.099 × 10.093; H2: 10.516 × 10.515; J3: 157 × 147. **Sem regressão** |
| Juntas do gabinete (12 planos em corte), V9 × V8 | dentro do ruído do renderizador em todos os planos (ex.: C2 12.194 × 12.217 px; H2 5.692 × 5.707 px), **exceto o C4**: junta topo × fundo 2.037 × 1.599 px (sensível 9.548 × 4.609). A diferença está nos quadros da aproximação nova (item 5) |
| AO nos cortes ilustrativos (12 planos), detector sensível, V9 × V8 | C2, C3, D1, G3, H1 e J3: ±1,7 %; D3 −29 %, G1 −19 %, D5 −3 %; G2 +7 % (pior quadro 0 blocos nos dois) e H2 +4,6 % (pior 4 × 3 blocos), ambos com itens novos no quadro. **C4: +60 % (744.656 × 464.450 px)**, só na aproximação (item 5) |
| Cintilação absoluta (31 planos) | igual ou menor que a V8, exceto: **C4** (item 5); I1 e D3 (mapas: bordas em movimento e itens novos, pior quadro do D3 = 5 blocos); A2 só fora do trecho mostrado (nos quadros exibidos, 6 × 15 blocos: melhor) |
| Rótulos × narração | 24 rótulos, 0 antes da palavra; resultado idêntico ao anterior |
| Composição em **todos os 4.537 quadros** (legendas, rótulos, cartões, avisos, lupa) | **0 problemas**; 865/865 ponteiros iguais ao modelo. Na V9a eram 901 porque os cartões do C4 saíam mais tarde |
| C4 → D1 | evaporador na mesma coluna (x 542 → 540 px); borda de cima a 368 → 432 px; escala 2,1×, com fusão de 0,30 s |
| Integridade do vídeo | 4.537 quadros, 30 fps, 151,233 s; AAC 48 kHz estéreo, 151,233 s; decodificação sem erro |

**Áudio, medido no AAC da V9** (`relatorios/validacao_audio_v9.json`):

| Medida | Resultado |
|---|---|
| Loudness | −14,10 LUFS |
| Pico verdadeiro | −1,68 dBTP |
| Voz − resto no celular simulado | pior −0,8 / p5 16,2 / mediana 28,8 dB |
| Mono | −0,01 dB |
| Fim | −45,6 dBFS |

- **É idêntico à variante "só passos" que você escolheu.** O pior caso de −0,8 dB vem de antes; ele já estava na
  mixagem aprovada da V8 e da V9a.
- **Sincronia:** o áudio do vídeo coincide com a mixagem aprovada, com defasagem de 0,00 ms em quatro pontos
  (correlação ≥ 0,9997).
- **Passos do I1:** os pousos de 118,22 s e 119,09 s caem a menos de 1 quadro do pouso do pé na animação (118,25 e
  119,12 s).
- **Narração:** o MP3 original está intacto (`fdedd877…`). Inteligibilidade igual à aprovada.

## 5. Achado novo: estroboscopia no fim do C4 (consequência da aproximação aprovada)

**Medida** (`medir_estrobo.py`, pela geometria):
- Na aproximação, a grade do condensador (lado direito) anda até **3,6 vezes o espaçamento dos arames por quadro**. Na
  V8 eram 0,84. São 34 quadros acima de 0,5, entre 47,16 e 48,23 s; acima de 0,5 o olho não distingue o sentido do
  movimento.
- Os tubos do evaporador também "tremem" na fase rápida.

**Em 1080:** o detector marca 16 de 28 quadros (q155–170), pior com 942 blocos. O mapa mostra só bordas em movimento e a
grade. **Não é z-fighting.**

**Teste A/B, desligado na V9:**
- **Técnica:** obturador de 180°, a mesma aprovada no C2 na rodada 8. São 5 sub-quadros por quadro, média em luz
  linear; o sub-quadro central é o quadro da V9 (diferença média de 1,0–1,4, dentro do ruído do renderizador).
- **Escopo:** só o C4, quadros 126–178.

| Medida (C4 q127–177, 540) | V9 | Com obturador |
|---|---|---|
| Blocos piscando (padrão) | 4.035 | **2.788 (−31 %)** |
| Pixels alternando (\|Δ\| > 30) | 794.976 | **553.870 (−30 %)** |
| Pior quadro | 280 blocos | 153 blocos |
| Nitidez (gradiente, obturador ÷ V9) | — | 0,63 no pico da velocidade; 0,96–0,99 quando a câmera desacelera |

- **Imagem:** a grade vira um borrão de movimento, como numa câmera real (`c4_q151_v9_x_obturador.jpg`).
- **O que não muda:** câmera, tempos e composição. Quadro inicial e final praticamente iguais.

**Recomendação:** aplicar o obturador no fim do C4 (126–178) no render definitivo.
- Custo extra em 1080: ≈ 2 h.
- Se você preferir, dá para aplicar ao C4 inteiro: muda só a fase rápida, porque com a câmera parada a nitidez é
  ≈ 1.

## 6. Testes curtos em 1080 × 1920 (trechos críticos modificados)

Configuração proposta para o definitivo; os quadros ficam em `episodio/quadros_final_r9v/`.
Registro: `relatorios/testes_1080_v9.json`.

| Trecho | s/quadro | Resultado |
|---|---|---|
| I1 q78–107 (pega, saída, volta da câmera) | 23,9 | só bordas em movimento (porta, braço, câmera); sem z-fighting |
| C4 q155–184 (fim da aproximação) | 37,3 | estroboscopia (item 5); sem z-fighting |
| A1 q4–29 (puxão) | 18,2 | só bordas da porta, da fresta e do braço; sem z-fighting |
| H2 q40–69 (corte com itens novos) | 25,1 | = rodada 8 aprovada nos mesmos quadros (detector: 8 × 9 blocos; porta × vedação: 815 × 817 px) |
| J3 q84–113 (corte sem leite) | 24,6 | = rodada 8: 0 blocos; porta × vedação 3 × 3 px |

**Nenhum defeito aparece só em 1080.**

## 7. O que não mudou

- **Narração:** MP3, cópia de mixagem e tempos das palavras.
- **Planos reaproveitados:** A3, D2, D4, E1–E4, F1, F2, G3z e J4 são os quadros da V8 (prova de reuso).
- **Planos alterados:** fora das mudanças aprovadas, câmeras, tempos e estrutura dos planos estão iguais.
- **Composição:** a da V9a; só o A4 em corte seco, como você escolheu.
- **Áudio:** fora dos passos do I1, idêntico ao aprovado (≤ −108,6 dBFS de diferença no WAV).
- **Encerramento:** sem vinheta, mascote ou assinatura.

## 8. Custo do render definitivo em 1080 (se aprovado)

- **Razão 1080/540 medida nos 5 trechos:** 3,0 a 5,3 (média ≈ 4).
- **Episódio inteiro:** ≈ 27–30 h, um processo por vez, mais ≈ 3,6 h do C2 com obturador (já aprovado) e ≈ 2 h se o C4
  ganhar obturador.
- **Armazenamento:** o contêiner é temporário. Render, montagem, verificação e master no git precisam acontecer na
  mesma sessão, com o vídeo final em partes < 95 MB se necessário.

## 9. Decisões para você

1. **Aprovar a V9** como base para o render definitivo.
2. **Fim do C4:**
   - aplicar o obturador de 180° nos quadros 126–178 (recomendado);
   - ou no C4 inteiro;
   - ou manter como está.
3. **Autorizar o render definitivo em 1080**, com a configuração dos testes curtos.

**Licença:** a narração da ElevenLabs foi gerada no plano gratuito, **sem uso comercial**, com atribuição obrigatória.
A licença da voz continua pendente. Os efeitos sonoros são os mesmos da V8: Mixkit, Commons CC0 e Freesound CC0.

**Nada publicado. Nenhuma voz gerada. Nenhum serviço contratado. Episódio 01 intacto. Render 1080 completo não iniciado.**
