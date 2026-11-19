# Mapa de substituição dos efeitos · Ep. 01 (som híbrido)

Cada grupo tem stems próprios em `episodio/stems/grupos/` (efeitos e ambiências), com a **mesma cadeia de mixagem** do episódio
(reverberação, nível, ducking, fade e master). Somados ao `resto`, reconstroem exatamente os stems de efeitos e ambiências
(erro máx. −132 dBFS). Dá para ouvir um grupo isolado, ou o episódio sem ele, e trocar só aquele grupo.

**Como trocar uma gravação depois da escuta (sem editar código e sem refazer animação):**
1. Coloque o arquivo novo em `episodio/som/bib/manual/`.
2. Em `episodio/som/substituicoes.json`, adicione o **ID original** (coluna "Gravação") apontando para o arquivo, com título, autor, URL e licença.
3. Rode `python3 som/som_hibrido.py && SUFIXO_REG=hibrido python3 som/registro_hibrido.py && SUFIXO_REG=hibrido python3 som/mapa_substituicao.py`.
4. A troca entra nos mesmos instantes, camadas e níveis. Só a montagem 2D é refeita para o vídeo de revisão.

Atenção: um mesmo ID pode ser usado em vários grupos (ex.: 3076, rangido do casco). A troca por ID vale para todos os usos dele.

## Estaleiro (ambiente, encaixe, solda, chapas, corte do casco)

- Stem: `stems/grupos/ep01_efeitos_estaleiro_hibrido.wav` · ativo de 23.58 a 41.38 s
- Stem: `stems/grupos/ep01_ambiencias_estaleiro_hibrido.wav` · ativo de 15.22 a 42.52 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 15.10 | 15.85 | 3074 · Inside the old boat shipyard ambience | não | ambiente de estaleiro (galpão de construção naval) |
| 15.10 | 15.85 | 812 · Construction welder | sim — no lugar de WWS Weldingonshipinfloatingdrydock | solda distante em outro ponto do casco (estaleiro real) |
| 23.60 | 2.20 | 783 · Submarine metal impact | não | encaixe da chapa: corpo grave de aço pesado |
| 23.60 | 1.95 | 2983 · Factory hit with echo | não | encaixe da chapa: batida metálica no galpão (com eco real) |
| 23.60 | 1.76 | 2980 · Factory metal hard hit | não | contato metálico duro (camada aguda) |
| 23.60 | 0.60 | sintese · reforço grave (síntese discreta) | síntese | peso da chapa no encaixe |
| 23.75 | 0.90 | 2603 · Electric welding and sparkles | não | arco elétrico de solda e faíscas (gravação real) |
| 24.00 | 0.80 | 2603 · Electric welding and sparkles | não | arco elétrico de solda e faíscas (gravação real) |
| 24.68 | 0.67 | 2603 · Electric welding and sparkles | não | arco elétrico de solda e faíscas (gravação real) |
| 24.85 | 0.65 | 2603 · Electric welding and sparkles | não | arco elétrico de solda e faíscas (gravação real) |
| 24.90 | 1.55 | 812 · Construction welder | não | solda ao fundo (bojo) |
| 25.10 | 1.99 | 814 · Construction welding tool | não | solda ao fundo (bojo) |
| 26.00 | 1.02 | 2754 · Metal tank door closing | não | chapas chegando ao costado e à proa (contatos selecionados) |
| 26.38 | 1.13 | 3158 · Thin metal plate drop | não | chapas chegando ao costado e à proa (contatos selecionados) |
| 26.80 | 1.95 | 2983 · Factory hit with echo | não | chapas chegando ao costado e à proa (contatos selecionados) |
| 27.22 | 1.02 | 2754 · Metal tank door closing | não | chapas chegando ao costado e à proa (contatos selecionados) |
| 28.65 | 1.60 | 783 · Submarine metal impact | não | chapas chegando ao costado e à proa (contatos selecionados) |
| 29.75 | 1.20 | 1167 · Swoosh wind passing | não | passagem de tempo do estaleiro (sopro suave) |
| 30.00 | 5.60 | 3074 · Inside the old boat shipyard ambience | não | estaleiro (navio já pronto) |
| 33.15 | 1.39 | 1523 · Heavy sliding door | não | proa se separando: aço pesado deslizando |
| 33.15 | 1.60 | sintese · reforço grave (síntese discreta) | síntese | massa da proa deslizando |
| 33.25 | 1.60 | 3076 · Ship hull creak | não | estrutura rangendo no corte |
| 35.00 | 7.10 | 2504 · Industrial machine hum | não | interior do casco vazio (zumbido industrial distante) |
| 37.00 | 1.00 | sintese · transição sutil (síntese) | síntese | células acendendo (brilho sutil, sem bipe) |
| 39.20 | 1.00 | sintese · transição sutil (síntese) | síntese | células acendendo (brilho sutil, sem bipe) |
| 39.60 | 1.20 | 3076 · Ship hull creak | não | estalo térmico no porão vazio |

## Guindastes (pórtico do estaleiro e portêineres)

- Stem: `stems/grupos/ep01_efeitos_guindastes_hibrido.wav` · ativo de 15.09 a 117.77 s
- Stem: `stems/grupos/ep01_ambiencias_guindastes_hibrido.wav` · ativo de 15.11 a 35.86 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 15.10 | 15.85 | 2504 · Industrial machine hum | sim — no lugar de WWS Shipyardcrane | guindaste de estaleiro ao fundo (Gotenius, Gotemburgo) |
| 15.10 | 15.20 | 2504 · Industrial machine hum | sim — no lugar de WWS Shipyardcrane | motor/translação do pórtico (guindaste de estaleiro real) seguindo a velocidade do carro |
| 15.10 | 15.20 | 1534 · Metallic door sliding | sim — no lugar de WWS Crane | carro rolando no trilho (ponte rolante real) |
| 15.23 | 1.40 | 3076 · Ship hull creak | não | cabos e estrutura rangendo na arrancada/freada |
| 20.93 | 1.40 | 3076 · Ship hull creak | não | cabos e estrutura rangendo na arrancada/freada |
| 23.20 | 1.40 | 3076 · Ship hull creak | não | cabos e estrutura rangendo na arrancada/freada |
| 30.00 | 5.60 | 2504 · Industrial machine hum | sim — no lugar de WWS Shipyardcrane | guindaste ao fundo |
| 94.55 | 22.65 | 2504 · Industrial machine hum | sim — no lugar de WWS Containershipgantrycrane | portêiner carregando o navio (guindaste real): carro, guincho e cabos seguem o movimento |
| 94.55 | 22.65 | 802 · Construction machine motor passing | sim — no lugar de WWS Mobileharbourcrane | guindastes vizinhos (guindaste portuário real, mais distante) |
| 100.70 | 0.90 | 3076 · Ship hull creak | não | cabos tensionando antes do pouso |
| 102.05 | 0.90 | 3076 · Ship hull creak | não | cabos tensionando antes do pouso |
| 103.55 | 0.90 | 3076 · Ship hull creak | não | cabos tensionando antes do pouso |

## Porto (ambiente, empilhadeiras, pousos de contêiner, água no casco)

- Stem: `stems/grupos/ep01_efeitos_porto_hibrido.wav` · ativo de 94.55 a 132.88 s
- Stem: `stems/grupos/ep01_ambiencias_porto_hibrido.wav` · ativo de 94.59 a 134.71 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 94.55 | 39.95 | 819 · Urban construction site ambiance | sim — no lugar de WWS ContainerTerminalatthePortofDortmund | ambiente de terminal de contêineres (gravação real) |
| 94.55 | 22.85 | 1621 · Truck driving steady | sim — no lugar de WWS Containerreachstackers | empilhadeiras de contêiner ao fundo |
| 94.55 | 39.95 | 1208 · Small waves harbor rocks | não | água junto ao cais |
| 94.55 | 22.65 | 1195 · Close sea waves loop | sim — no lugar de WWS Smallwaves | água batendo no casco enquanto o navio afunda com a carga |
| 101.60 | 1.02 | 2754 · Metal tank door closing | não | contêiner pousando (batida de caixa metálica) |
| 101.60 | 1.40 | 783 · Submarine metal impact | não | peso do contêiner no pouso |
| 102.95 | 1.02 | 2754 · Metal tank door closing | não | contêiner pousando (batida de caixa metálica) |
| 102.95 | 1.40 | 783 · Submarine metal impact | não | peso do contêiner no pouso |
| 104.45 | 1.02 | 2754 · Metal tank door closing | não | contêiner pousando (batida de caixa metálica) |
| 104.45 | 1.40 | 783 · Submarine metal impact | não | peso do contêiner no pouso |
| 105.45 | 11.95 | 819 · Urban construction site ambiance | sim — no lugar de WWS ContainerTerminalatthePortofDortmund | terminal em atividade (tempo acelerado) |
| 107.30 | 1.95 | 2983 · Factory hit with echo | não | contato distante de contêiner (só alguns, no tempo acelerado) |
| 110.10 | 1.95 | 2983 · Factory hit with echo | não | contato distante de contêiner (só alguns, no tempo acelerado) |
| 113.40 | 1.95 | 2983 · Factory hit with echo | não | contato distante de contêiner (só alguns, no tempo acelerado) |
| 117.20 | 17.30 | 1195 · Close sea waves loop | sim — no lugar de WWS Smallwaves | água no casco (calado / marcas) |
| 118.90 | 2.00 | 1208 · Small waves harbor rocks | não | cota do calado sobe (marulho junto à quilha) |
| 130.40 | 2.60 | sintese · transição sutil (síntese) | síntese | marcas de calado acendendo (um único brilho sutil para as 5 linhas) |

## Dique (comporta, jatos, enchimento)

- Stem: `stems/grupos/ep01_efeitos_dique_hibrido.wav` · ativo de 41.67 a 48.74 s
- Stem: `stems/grupos/ep01_ambiencias_dique_hibrido.wav` · ativo de 41.3 a 48.82 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 41.30 | 7.15 | 2509 · Metal industry ambience | sim — no lugar de WWS Adjustingadrydock | dique flutuante sendo ajustado (bombas e água, gravação real) |
| 41.70 | 2.50 | 783 · Submarine metal impact | não | comporta/válvulas abrindo (impacto metálico grave) |
| 41.70 | 1.00 | sintese · reforço grave (síntese discreta) | síntese | peso da comporta |
| 41.70 | 2.50 | 3029 · Heavy close waterfall | não | jatos de água entrando no dique (cascata forte) |
| 42.00 | 6.20 | 1303 · Water flowing | sim — no lugar de WWS Waterintakepumpingstation | água correndo pelas tubulações de enchimento (estação de bombeamento real) |
| 42.30 | 3.80 | 1208 · Small waves harbor rocks | não | água alcançando o casco e os picadeiros |
| 43.40 | 4.60 | 2461 · Strong flowing waters noise | não | enchimento contínuo, cada vez mais grave |
| 46.10 | 1.40 | 3076 · Ship hull creak | não | estrutura alivia quando o peso deixa os picadeiros |
| 46.10 | 1.40 | sintese · reforço grave (síntese discreta) | síntese | casco se desprende dos picadeiros (leve) |
| 46.40 | 1.80 | 1208 · Small waves harbor rocks | não | casco livre: água ao redor |

## Inundação da avaria (ruptura, jato, porão enchendo, rangidos, divisórias)

- Stem: `stems/grupos/ep01_efeitos_inundacao_hibrido.wav` · ativo de 134.93 a 155.1 s
- Stem: `stems/grupos/ep01_ambiencias_inundacao_hibrido.wav` · ativo de 134.01 a 137.24 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 134.00 | 3.20 | 1189 · Sea waves ambience | não | mar (exterior do casco) |
| 134.90 | 1.76 | 2980 · Factory metal hard hit | não | ruptura: impacto metálico localizado |
| 134.90 | 1.20 | 200 · Industrial metal sliding door | não | ruptura: aço rasgando/raspando |
| 134.95 | 0.60 | sintese · reforço grave (síntese discreta) | síntese | ruptura (peso) |
| 135.00 | 2.00 | 1877 · Sink underwater drain | não | bolhas sugadas pelo rombo |
| 135.30 | 5.85 | 1321 · Deep water bubbles | não | bolhas |
| 136.90 | 9.50 | 3029 · Heavy close waterfall | não | água sob pressão entrando pelo rombo (cascata forte) |
| 136.90 | 9.50 | 3140 · Long giant water pour into vat | não | jorro despejando no porão |
| 137.00 | 18.00 | 2509 · Metal industry ambience | não | tensão grave crescente (alivia após as divisórias) |
| 137.20 | 10.60 | 2461 · Strong flowing waters noise | não | turbulência do porão enchendo |
| 137.20 | 10.60 | 1877 · Sink underwater drain | não | borbulhar e gorgolejo da água subindo |
| 137.60 | 1.68 | 1198 · Sea water splash | não | água golpeando anteparas e piso |
| 138.50 | 1.88 | 3216 · Water hit | não | água golpeando anteparas e piso |
| 139.50 | 1.60 | 3076 · Ship hull creak | não | casco rangendo sob a carga crescente |
| 139.60 | 1.28 | 1311 · Water splash | não | água golpeando anteparas e piso |
| 140.90 | 1.68 | 1198 · Sea water splash | não | água golpeando anteparas e piso |
| 142.20 | 1.88 | 3216 · Water hit | não | água golpeando anteparas e piso |
| 142.30 | 1.60 | 3076 · Ship hull creak | não | casco rangendo sob a carga crescente |
| 144.90 | 1.60 | 3076 · Ship hull creak | não | casco rangendo sob a carga crescente |
| 146.80 | 1.60 | 3076 · Ship hull creak | não | casco rangendo sob a carga crescente |
| 148.40 | 1.60 | 3076 · Ship hull creak | não | casco rangendo sob a carga crescente |
| 149.70 | 1.60 | 3076 · Ship hull creak | não | casco rangendo sob a carga crescente |
| 151.05 | 2.40 | 783 · Submarine metal impact | não | divisórias estanques: batida firme e calma (aço pesado) |
| 151.05 | 1.20 | sintese · reforço grave (síntese discreta) | síntese | divisórias (peso) |

## Demais efeitos (abertura, empuxo, retomada, experimento, conclusão)

85 usos, no stem `resto`. A lista completa por gravação está em `som/fontes_efeitos_hibrido.md`.

