# Mapa de substituição dos efeitos · Ep. 01 (som refinado)

Cada grupo tem stems próprios em `episodio/stems/grupos/` (efeitos e ambiências), com a **mesma cadeia de mixagem** do episódio
(reverberação, nível, ducking, fade e master). Somados ao `resto`, reconstroem exatamente os stems de efeitos e ambiências
(erro máx. −132 dBFS). Dá para ouvir um grupo isolado, ou o episódio sem ele, e trocar só aquele grupo.

**Como trocar uma gravação depois da escuta (sem editar código e sem refazer animação):**
1. Coloque o arquivo novo em `episodio/som/bib/manual/`.
2. Em `episodio/som/substituicoes.json`, adicione o **ID original** (coluna "Gravação") apontando para o arquivo, com título, autor, URL e licença.
3. Rode `python3 som/som_refinado.py && SUFIXO_REG=refinado python3 som/registro_hibrido.py && SUFIXO_REG=refinado python3 som/mapa_substituicao.py`.
4. A troca entra nos mesmos instantes, camadas e níveis. Só a montagem 2D é refeita para o vídeo de revisão.

Atenção: um mesmo ID pode ser usado em vários grupos (ex.: 3076, rangido do casco). A troca por ID vale para todos os usos dele.

## Estaleiro (ambiente, encaixe, solda, chapas, corte do casco)

- Stem: `stems/grupos/ep01_efeitos_estaleiro_refinado.wav` · ativo de 23.58 a 40.71 s
- Stem: `stems/grupos/ep01_ambiencias_estaleiro_refinado.wav` · ativo de 15.02 a 41.89 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 15.10 | 16.40 | 3074 · Inside the old boat shipyard ambience | não | ambiente de estaleiro (galpão de construção naval) |
| 23.60 | 1.60 | 783 · Submarine metal impact | não | encaixe da chapa: corpo grave de aço |
| 23.60 | 1.20 | 2983 · Factory hit with echo | não | encaixe: batida metálica (eco real do galpão) |
| 23.60 | 1.76 | 2980 · Factory metal hard hit | não | encaixe: contato agudo |
| 23.60 | 0.60 | sintese · reforço grave (síntese discreta) | síntese | peso da chapa no encaixe |
| 23.75 | 0.86 | 2603 · Electric welding and sparkles | não | arco de solda e faíscas (só no cordão, com o brilho) |
| 24.00 | 0.76 | 2603 · Electric welding and sparkles | não | arco de solda e faíscas (só no cordão, com o brilho) |
| 24.68 | 0.63 | 2603 · Electric welding and sparkles | não | arco de solda e faíscas (só no cordão, com o brilho) |
| 24.85 | 0.61 | 2603 · Electric welding and sparkles | não | arco de solda e faíscas (só no cordão, com o brilho) |
| 24.90 | 1.17 | 812 · Construction welder | não | arco de solda e faíscas (só no cordão, com o brilho) |
| 25.10 | 1.36 | 814 · Construction welding tool | não | arco de solda e faíscas (só no cordão, com o brilho) |
| 26.00 | 0.90 | 2754 · Metal tank door closing | não | chapa encostando no casco (contato) |
| 26.38 | 0.90 | 3158 · Thin metal plate drop | não | chapa encostando no casco (contato) |
| 26.80 | 0.90 | 2983 · Factory hit with echo | não | chapa encostando no casco (contato) |
| 27.22 | 0.90 | 2754 · Metal tank door closing | não | chapa encostando no casco (contato) |
| 28.65 | 0.90 | 3158 · Thin metal plate drop | não | chapa encostando no casco (contato) |
| 29.75 | 1.20 | 1167 · Swoosh wind passing | não | passagem de tempo "Meses depois" (sopro suave, único) |
| 30.30 | 5.90 | 3074 · Inside the old boat shipyard ambience | não | estaleiro (navio pronto) |
| 33.15 | 1.39 | 1523 · Heavy sliding door | não | proa se separando: aço pesado deslizando |
| 33.25 | 1.40 | 3076 · Ship hull creak | não | estrutura rangendo no corte |
| 35.00 | 7.75 | 2504 · Industrial machine hum | não | interior do casco vazio (zumbido distante) |
| 37.00 | 1.00 | sintese · textura gráfica sutil (síntese) | síntese | células acendendo (brilho sutil) |
| 39.20 | 1.00 | sintese · textura gráfica sutil (síntese) | síntese | células acendendo (brilho sutil) |
| 39.60 | 1.00 | 3076 · Ship hull creak | não | estalo térmico no porão vazio |

## Guindastes (pórtico do estaleiro e portêineres)

- Stem: `stems/grupos/ep01_efeitos_guindastes_refinado.wav` · ativo de 15.1 a 109.34 s
- Stem: `stems/grupos/ep01_ambiencias_guindastes_refinado.wav` · ativo de 14.76 a 35.34 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 15.10 | 16.40 | 2504 · Industrial machine hum | sim — no lugar de WWS Shipyardcrane | guindastes distantes (fundo) |
| 15.10 | 16.96 | 2504 · Industrial machine hum | sim — no lugar de WWS Shipyardcrane | motor de translação do pórtico: segue velocidade e aceleração do carro; para quando o carro para |
| 15.10 | 16.66 | 1534 · Metallic door sliding | não | rodas do carro rolando no trilho (só em movimento) |
| 15.10 | 17.42 | 2139 · Industrial hum loop | não | guincho de içamento: segue a carga subindo/descendo |
| 15.27 | 1.20 | 3076 · Ship hull creak | não | cabos rangendo na arrancada/frenagem da carga |
| 20.93 | 1.20 | 3076 · Ship hull creak | não | cabos rangendo na arrancada/frenagem da carga |
| 30.30 | 5.90 | 2504 · Industrial machine hum | sim — no lugar de WWS Shipyardcrane | guindastes distantes |
| 94.55 | 25.01 | 2504 · Industrial machine hum | sim — no lugar de WWS Containershipgantrycrane | portêiner: motores do carro e do guincho seguem o movimento (param quando ele para) |
| 94.55 | 24.56 | 802 · Construction machine motor passing | sim — no lugar de WWS Mobileharbourcrane | portêineres vizinhos (mais distantes, só em movimento) |
| 97.55 | 0.80 | 3076 · Ship hull creak | não | cabos tensionando (arrancada/frenagem do spreader) |
| 100.25 | 0.80 | 3076 · Ship hull creak | não | cabos tensionando (arrancada/frenagem do spreader) |

## Porto (ambiente, empilhadeiras, pousos de contêiner, água no casco)

- Stem: `stems/grupos/ep01_efeitos_porto_refinado.wav` · ativo de 94.55 a 132.86 s
- Stem: `stems/grupos/ep01_ambiencias_porto_refinado.wav` · ativo de 94.22 a 134.41 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 94.55 | 40.65 | 819 · Urban construction site ambiance | sim — no lugar de WWS ContainerTerminalatthePortofDortmund | ambiente de porto (fundo) |
| 94.55 | 23.85 | 1621 · Truck driving steady | sim — no lugar de WWS Containerreachstackers | veículos do pátio ao fundo |
| 94.55 | 40.65 | 1208 · Small waves harbor rocks | não | água junto ao cais (leve) |
| 94.55 | 22.65 | 1195 · Close sea waves loop | sim — no lugar de WWS Smallwaves | água no casco enquanto o navio afunda com a carga |
| 101.60 | 0.60 | 2754 · Metal tank door closing | não | contêiner encaixa (contato metálico) |
| 101.63 | 0.45 | 3158 · Thin metal plate drop | não | vibração curta da caixa após o encaixe |
| 102.95 | 0.60 | 2754 · Metal tank door closing | não | contêiner encaixa (contato metálico) |
| 102.98 | 0.45 | 3158 · Thin metal plate drop | não | vibração curta da caixa após o encaixe |
| 104.45 | 0.60 | 2754 · Metal tank door closing | não | contêiner encaixa (contato metálico) |
| 104.48 | 0.45 | 3158 · Thin metal plate drop | não | vibração curta da caixa após o encaixe |
| 105.45 | 12.95 | 819 · Urban construction site ambiance | sim — no lugar de WWS ContainerTerminalatthePortofDortmund | porto em atividade (tempo acelerado) |
| 107.30 | 0.90 | 2983 · Factory hit with echo | não | contato distante de contêiner |
| 110.10 | 0.90 | 2983 · Factory hit with echo | não | contato distante de contêiner |
| 113.40 | 0.90 | 2983 · Factory hit with echo | não | contato distante de contêiner |
| 117.20 | 18.00 | 1195 · Close sea waves loop | sim — no lugar de WWS Smallwaves | água no casco (calado e marcas, leve) |
| 118.90 | 2.00 | 1208 · Small waves harbor rocks | não | cota do calado sobe (marulho junto à quilha) |
| 130.40 | 2.60 | sintese · textura gráfica sutil (síntese) | síntese | marcas acendendo (um único brilho sutil) |

## Dique (comporta, jatos, enchimento)

- Stem: `stems/grupos/ep01_efeitos_dique_refinado.wav` · ativo de 41.45 a 48.71 s
- Stem: `stems/grupos/ep01_ambiencias_dique_refinado.wav` · ativo de 41.15 a 48.5 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 41.45 | 0.90 | 2757 · Metal tank gear shift | não | mecanismo da válvula (destrava) |
| 41.55 | 7.65 | 2509 · Metal industry ambience | sim — no lugar de WWS Adjustingadrydock | bombas do dique (fundo) |
| 41.70 | 1.40 | 2982 · Industrial ambience hits | não | comporta/válvula abrindo (batida metálica) |
| 41.70 | 0.90 | sintese · reforço grave (síntese discreta) | síntese | peso da comporta (grande estrutura) |
| 41.70 | 2.70 | 3029 · Heavy close waterfall | não | jatos de água entrando no dique (principal) |
| 43.20 | 5.20 | 2461 · Strong flowing waters noise | não | enchimento do dique: mais grave e calmo conforme o nível sobe |
| 46.10 | 1.20 | 3076 · Ship hull creak | não | casco deixa os picadeiros (rangido leve) |
| 46.50 | 1.80 | 1208 · Small waves harbor rocks | não | casco livre: água em volta (leve) |

## Inundação da avaria (ruptura, jato, porão enchendo, rangidos, divisórias)

- Stem: `stems/grupos/ep01_efeitos_inundacao_refinado.wav` · ativo de 134.94 a 154.58 s
- Stem: `stems/grupos/ep01_ambiencias_inundacao_refinado.wav` · ativo de 133.63 a 137.4 s

| Instante (s) | Duração (s) | Gravação (ID · nome) | Reserva? | Uso |
|---|---|---|---|---|
| 134.00 | 4.20 | 1189 · Sea waves ambience | não | mar (exterior do casco) |
| 134.90 | 1.76 | 2980 · Factory metal hard hit | não | ruptura: impacto metálico localizado |
| 134.90 | 1.00 | 200 · Industrial metal sliding door | não | ruptura: aço rasgando |
| 134.95 | 0.60 | sintese · reforço grave (síntese discreta) | síntese | ruptura (peso) |
| 135.00 | 1.80 | 1877 · Sink underwater drain | não | bolhas sugadas pelo rombo |
| 136.90 | 9.50 | 3029 · Heavy close waterfall | não | jato de água sob pressão entrando pelo rombo (principal) |
| 137.00 | 18.00 | 2509 · Metal industry ambience | não | tensão grave da inundação (alivia nas divisórias) |
| 137.20 | 10.10 | 2461 · Strong flowing waters noise | não | porão enchendo (cresce com o nível) |
| 137.60 | 1.00 | 1198 · Sea water splash | não | água golpeando anteparas |
| 139.50 | 1.40 | 3076 · Ship hull creak | não | casco rangendo sob a carga |
| 139.60 | 1.00 | 1311 · Water splash | não | água golpeando anteparas |
| 142.20 | 1.00 | 3216 · Water hit | não | água golpeando anteparas |
| 142.30 | 1.40 | 3076 · Ship hull creak | não | casco rangendo sob a carga |
| 146.80 | 1.40 | 3076 · Ship hull creak | não | casco rangendo sob a carga |
| 149.70 | 1.40 | 3076 · Ship hull creak | não | casco rangendo sob a carga |
| 151.05 | 1.40 | 2982 · Industrial ambience hits | não | divisórias estanques: batida firme e calma |

## Demais efeitos (abertura, empuxo, retomada, experimento, conclusão)

73 usos, no stem `resto`. A lista completa por gravação está em `som/fontes_efeitos_refinado.md`.

