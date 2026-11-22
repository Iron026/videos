# Ep. 02 · Relatório da rodada 5 (polimento visual + primeira mixagem)

**Nada publicado.** Nenhuma voz gerada, nenhum crédito gasto, nenhum serviço contratado. O Ep. 01 não foi alterado
(`git diff` vazio). O render definitivo em 1080 × 1920 **não foi iniciado**.
- **Narração:** SHA-256 `fdedd877…05726ee`, conferido, arquivo intocado. A mixagem usa uma cópia decodificada.
- **Preservados:** roteiro, palavras (`roteiro/palavras.json`), modelo científico, legendas.
- **Estrutura idêntica à V4:** 39 planos, mesmos `id`, `t0`, `t1` e `dur` (diferenças: nenhuma).
- **Vídeo:** 4.537 quadros, 151,233 s (igual à V4).

## Entregas
| Arquivo | O que é |
|---|---|
| `episodio/ep02_animatic.mp4` | **V5**: 540 × 960, 30 qps, 151,23 s, primeira mixagem (AAC 48 kHz). SHA-256 `d47c4eb7…` |
| `episodio/ep02_v4_x_v5_lado_a_lado.mp4` | V4 \| V5 lado a lado, episódio inteiro, áudio da V5 |
| `relatorios/antes_depois_v5_1…6.jpg` | Antes × depois de todos os 39 planos, no mesmo instante (V4 em cima, V5 embaixo) |
| `som/ab/ab_*.mp4` (6 trechos) | A/B sonoro: **A** = só narração · **B** = mixagem completa, com a voz no **mesmo nível** |
| `som/stems/*.flac` | Stems: voz (cópia de mixagem), efeitos, mecanismo, ambiências |
| `relatorios/licencas_ep02.md` | Registro de arquivos e licenças |
| `ciencia/verificacao_g3.json` | Verificação do G3 contra o modelo e a narração |
| `relatorios/v4_x_v5_montado.json`, `cintilacao_v4.json`, `cintilacao_v5.json`, `som/validacao_audio.json`, `som/mix_ep02.json`, `som/ab/ab_trechos.json` | Medidas |

## 1. Acabamento visual
| Área | O que mudou |
|---|---|
| **Luz da cozinha** | Reflexos vêm da **própria cozinha** (ambiente capturado da cena) e as luzes de área projetam sombras suaves (contato no piso, sob armários e prateleiras). AO com raio de 35 cm, em vez de 2,5 m: as sombras de contato ficaram localizadas |
| **Dois modos de luz** | A captura de ambiente escurecia metais (evaporador) e as sombras escureciam interiores em corte. Diagnóstico feito ligando e desligando cada recurso. Planos em corte e esquemas (C2–H, J3, F2, lupa) usam a **luz técnica** da V4; a cozinha usa a luz nova |
| **Cenário** | Porcelanato 60 × 60 cm com rejunte, teto com luminária, parede frontal com vão de porta, parede direita, mesa com duas cadeiras, quadro. **Nenhum objeto na linha de visão** dos planos técnicos (testes de geometria passando) |
| **Materiais** | Gabinete com verniz (clearcoat), forro, compressor e armários refinados. **Mesmas temperaturas e cores didáticas**: a paleta térmica não mudou |
| **Revelação (C2)** | Corte seco em **33,92 s** e pulso **intactos**. Hierarquia visual: depois do corte, o que não é circuito escurece até 27 % (uniforme `uFoco`), e compressor, tubos e serpentinas ficam em destaque |

**Diferença média V4 × V5 por plano (0–255, 4 quadros por plano):** planos da cozinha 12–40 (luz nova); planos técnicos
1–4 (só materiais e AO: D1 1,6 · D3 1,1 · D4 2,0 · D5 1,5 · E1 1,9 · F2 1,6 · H1 2,7 · H2 3,4 · J3 2,7); G3 59 (reenquadrado,
com lupa).

## 2. Personagem
**Aparência fundamental e participação mantidas:** mesmos planos (A1, A2, A4, I1), mesmas cores e proporções.
- **Mãos:** antes eram blocos; agora têm palma, quatro dedos e polegar.
- **Roupa:**
  - punhos e barra canelados no suéter, com textura de malha discreta;
  - calça mais fosca.
- **Caminhada:**
  - **pés plantados**, sem deslizar no chão: o tornozelo fica parado no apoio e o joelho resolve por IK;
  - quadril corrigido (antes agachava 3 cm);
  - apoio calcanhar–ponta.
- **Vida:** respiração parada e piscadas.
- **Contraplano de A4:** o fundo era céu e parede lisa. Agora é a **cozinha**: teto, parede com quadro, mesa e cadeira.
- **Para sua avaliação:** com os dedos novos, a mão no queixo (A4) ficou **aberta, com os dedos para cima**. Na V4 aprovada
  era um punho. Se preferir o punho, a correção é localizada (pose dos dedos só em A4).

## 3. G3: capilar (pendência visual principal)
- **Plano geral:**
  - a geladeira inteira em corte;
  - o capilar **real**, do filtro secador ao evaporador;
  - o marcador (manômetro) percorrendo o tubo, com o ponteiro caindo de "alta" para "baixa".
- **Lupa:** ampliação localizada e declarada ("Lupa: canal ampliado (esquema)"). O canal esticado usa a **mesma tabela
  do modelo**, ponto a ponto.
- **O que a lupa mostra:**
  - líquido a 33 °C e 5,31 bar;
  - primeiro vapor em s = 0,532;
  - mistura a −20 °C, 0,725 bar e x = 0,33, com entalpia constante.
- **Rótulos:** presos ao **ponto físico** de cada estado.

**Verificação automática (`ciencia/verificar_g3.py`, lê o que foi EXPORTADO): aprovada.**
| Critério | Resultado |
|---|---|
| Marcador dentro do quadro o tempo todo | sim (v de 0,44 a 0,92) |
| Marcador avança sem voltar | sim |
| Centro da lupa = ponto do marcador | sim, até s = 0,885; depois a lupa para antes da ponta do tubo (borda em s = 0,999) |
| "líquido" aponta fluido sem vapor | x = 0,000 |
| "começa a evaporar" no início da evaporação | s = 0,532 (x = 0,002) |
| "mistura fria" aponta fluido abaixo de 0 °C | −5,9 °C |
| Início da evaporação × narração | o marcador chega a s = 0,532 em 104,55 s, entre "parte" (104,29) e "evapora" (105,16) |
| Saída × narração | chega ao fim em 106,85 s; "mistura" em 106,72 (+0,13 s) |

**Três erros meus achados e corrigidos por esta verificação:**
1. Na primeira câmera, o marcador ficava **fora do quadro** em "A pressão cai bruscamente" (o trecho enrolado do capilar
   estava abaixo da borda). Câmera recuada 1,6×, mesma direção.
2. A lupa mirava 0,083 em s **à frente** do marcador, e "líquido" chegou a apontar fluido com 1,5 % de vapor.
3. "mistura fria" apontava fluido a **+9 °C**: os rótulos acompanhavam a câmera, não o fenômeno.

Também corrigi um erro do **verificador** (ele supunha uma câmera perpendicular ao tubo) antes de mexer na cena.

## 4. Som (primeira mixagem)
- **Sistema modular do Ep. 01 reaproveitado:**
  - stems separados, com ganho fixo por stem;
  - ducking multibanda pela voz;
  - master fixo nas comparações A/B;
  - sons novos com gerador aleatório isolado.
  - O módulo de síntese do Ep. 01 é **lido sem alteração**.
- **Eventos ligados às curvas da animação:**
  - **Compressor:** zumbido real em todo o episódio, com volume pela **distância real da câmera** ao compressor. Na
    cozinha fica abafado (−9 dB e passa-baixas de 700 Hz, gabinete entre a câmera e o compressor). Em E3 ("câmera
    lenta") toca a 0,75× de rotação.
  - **Porta:**
    - abre em A1 e I1 no instante em que a vedação descola (ataque medido na gravação: 0,315 s);
    - fecha em C1 com a batida no instante em que o ângulo chega a zero.
  - **Passos:** cinco pousos medidos na gravação, alinhados aos pés plantados do personagem em I1.
  - **Evaporador:** gorgolejo real nos planos do evaporador, pela distância.
  - **Capilar (G3):** chiado **sintetizado**, discreto (−24 dB), subindo em "parte". Não havia gravação real adequada.
- **Voz:**
  - **Compressão suave na cópia de mixagem:** limiar no percentil 90 do nível da própria fala (−16,4 dBFS), razão 2:1.
    Média na fala de **−0,4 dB**; máximo de −4,7 dB, só nos picos.
  - **Uma tentativa anterior foi descartada:** limiar de −26 dBFS, que chegava a −11,4 dB e comprimia mais de 75 % da
    fala.
  - **Limitador:** máximo de −3,86 dB. Passa de 1 dB em **0,52 %** do tempo e de 3 dB em 0,013 %.

**Validação técnica medida no AAC do vídeo:**
| Meta | Medido |
|---|---|
| −14 LUFS ± 0,5 | **−14,1** |
| pico verdadeiro ≤ −1,5 dBTP | **−1,68** |
| mono sem perda | **−0,01 dB** |
| voz ≥ 10 dB acima do resto no celular simulado (p5) | **16,2 dB** (mediana 28,8) |
| silêncio no fim | último 0,5 s a −45,5 dBFS |

**Janelas abaixo de 10 dB:** 7 de 370, todas em **pausas** (voz da janela entre −37 e −44 dBFS, cauda de respiração).
Exemplos:
- **78,0 s:** "eletricidade." termina em 77,94 e "Ele" começa em 78,39.
- **119,0 s:** um passo do personagem cai na pausa antes de "O calor".

Nenhuma palavra fica coberta.

**A/B com a narração no mesmo nível** (A = só voz, B = mixagem; mesmo master +5,45 dB; LUFS da voz igual em A e B; o stem
de voz difere no máximo 1,5·10⁻⁴, ≈ −76 dBFS):
| Trecho | LUFS total A → B | Resto (B) | Voz − resto no celular: pior / mediana |
|---|---|---|---|
| Abertura 0–10,5 s | −14,49 → −14,41 | −32,2 | 13,7 / 28,3 dB |
| Revelação 28–38,5 s | −14,26 → −14,32 | −31,7 | 16,8 / 27,7 dB |
| Compressor 74–87 s | −14,07 → −13,76 | −23,6 | −0,8 (pausa em 78,0 s) / 24,6 dB |
| Capilar 101,8–107,6 s | −14,86 → −14,87 | −33,4 | 18,8 / 29,8 dB |
| Porta aberta 115–124,5 s | −14,27 → −14,26 | −27,8 | 5,3 (pausa em 119,0 s) / 29,2 dB |
| Final 145–151,2 s | −14,77 → −14,74 | −36,3 | 16,9 / 29,7 dB |

**Eu não escuto.** As escolhas das gravações foram por medição (estabilidade, energia grave, transientes, ausência de
fala) e por título e autor. A aprovação auditiva é sua.

## 5. Verificações de render
- **Integridade:** 42 planos renderizados no perfil econômico (escala 0,25, AO 8), sem nenhum quadro ruim (não-preto,
  integridade).
- **Cintilação (detector absoluto)**, aplicado à V5 e à V4 com o mesmo critério:
  - as contagens repetem as da V4 plano a plano (A1 13 × 13, C2 57 × 58, D4 47 × 47, H1 54 × 54…);
  - pelos mapas de cintilação, são **falsos positivos já conhecidos**:
    - arames finos do condensador em movimento (C3, E1, H1, H2), serrilhado em 270 px;
    - textura do fluido escoando (D4, F2);
    - personagem (A4, I1).
- **Z-fighting:**
  - **Regressão no G3:** 22 quadros piscando (0 na V4). Causa medida: a face de trás do painel da porta (y = GY0 − 0,001)
    **coincide** com a face da frente da vedação. Pelo corte, a câmera nova via as duas de raspão. A geometria vem da V1;
    a câmera nova só expôs o defeito.
  - **Correção:** painel recuado 0,5 mm. Resultado: **0 quadros** no G3.
  - **Teste nativo em 540 × 960:** três quadros seguidos estáveis.
  - **Fora do G3**, o vídeo montado não mudou (diferença média 0,039, ruído de codificação).
- **Defeito antigo, mesma causa, no J3** (43 quadros, igual à V4). A correção ficou **desligada** ali até a sua decisão
  (`CORRECAO_PORTA = {'G3'}`).
- **Testes nativos 540 × 960** (AO 16, MSAA 4×) em A1, C2, D3, I1 e G3: sem serrilhado nem acne de sombra visível.
- **Ciência e geometria:**
  - `ciencia/testes_ciclo.py`: 10/10;
  - `blender/testes_cena.py`: todos passaram (folgas entre tubos ≥ 15 mm, espiras do capilar separadas, nada atravessando
    o compressor).

## 6. O que não mudou (medido)
- Roteiro, narração (hash), palavras, legendas, cortes e duração. Estrutura idêntica à V4.
- **Revelação:** corte seco em 33,92 s e trajetória do pulso (mesmas curvas).
- **Cores didáticas:** mesma paleta térmica e mesmas temperaturas.
- **Personagem:** mesma aparência e mesmos planos.
- **Episódio 01:** intocado.

## 7. Pendências para a etapa definitiva
1. **Sua decisão:**
   - ligar a correção da porta no **J3** (e, por segurança, em todos os planos);
   - mão no queixo de A4: aberta ou punho.
2. **Linha vertical fina e fixa** no interior do G3 em 540 nativo, possivelmente a borda de uma peça no plano de corte. Não
   pisca. Causa ainda não investigada.
3. **Áudio:** a trilha passa 7 ms do último quadro (cortar no `trocar_audio`/master).
4. **Sons:** as prévias HQ do Freesound são MP3 de 128 kb/s. Para o definitivo:
   - baixar os originais (exige login gratuito no Freesound; não fiz por ser uma conta);
   - ou aceitar as prévias.
   - O chiado do capilar é síntese: trocar por gravação real, se aparecer uma adequada.
5. **Narração:** licença **pendente**. Plano da ElevenLabs não confirmado; tratada como gratuita (sem uso comercial,
   atribuição obrigatória). Não monetizar sem resolver.
6. **Escala e verificação:**
   - G3 em 1080: verificar a legibilidade da lupa e do marcador no celular.
   - Detector absoluto no episódio todo em 1080, com quadros consecutivos.
7. **Teste em 1080** dos trechos críticos (C2, G3, D4, E1) antes do render definitivo, que continua aguardando a sua
   aprovação.

**Limites:** eu meço; não assisto nem escuto como uma pessoa. Os quadros renderizados ficam no contêiner temporário e se
perdem no fim da sessão; código, cenas, mixagem, stems (FLAC) e vídeos estão no git.
