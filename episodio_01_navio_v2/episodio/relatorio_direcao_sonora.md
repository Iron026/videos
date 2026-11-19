# Ep. 01 · Refinamento da direção sonora (comparativos para avaliação)

**Entrega desta etapa:** `episodio/ep01_comparativo_som_refinado.mp4` (222,8 s).
- **Formato:** cada trecho toca primeiro com o **SOM ANTERIOR** e depois com o **SOM REFINADO**, com a **mesma imagem** (revisão aprovada) e a **mesma narração**.
- **Níveis comparáveis:** as duas mixagens estão a −14 LUFS. A refinada recebe −0,16 dB para que a **narração fique exatamente no mesmo nível** (−14,23 LUFS nas duas). O que muda entre elas é só o som da cena.

| # | Trecho | Tempo |
|---|---|---|
| 1 | Abertura e bloco na água | 0–15,1 s |
| 2 | Dique e empuxo | 40,8–64 s |
| 3a | Guindaste e solda (estaleiro) | 15,1–30,6 s |
| 3b | Guindastes e carregamento | 94,6–118 s |
| 4 | Avaria e inundação | 134–154,7 s |
| 5 | Conclusão | 154,6–168 s |

**Escopo:**
- Só som e mixagem: imagem, cenas, física, roteiro, narração e tempos **não foram alterados**.
- A montagem completa **não foi refeita**: ela será feita depois da sua avaliação, a partir do master de imagem (`trocar_audio.py`, ~75 s, sem render 3D).
- O som anterior continua intacto (mesmo SHA-256) para comparação.
- Nada foi publicado e o render de 1080 × 1920 não foi iniciado.

> ⚠️ A narração segue do plano gratuito da ElevenLabs: uso não comercial e atribuição obrigatória. O episódio **não está licenciado para exploração comercial** (`voz/LICENCA_NARRACAO.md`).

## Limitações

- **Referência (Desmontando o Mundo):** nova tentativa nesta etapa, e o YouTube continua sem entregar os vídeos a este ambiente. A página responde sem conteúdo; antes pedia login "para confirmar que não é um robô". **Não assisti nem escutei nada do canal** e não extraí material. Nada aqui é análise da referência; segui os princípios que você descreveu: ação física, narração, efeito e silêncio.
- **Não escuto o resultado.** Tudo abaixo são medições objetivas. Se o timbre convence, e se cada ajuste soa natural, só a sua escuta decide.

## 1. Menos água

**Método:**
1. Toda gravação de água passou a ser registrada numa categoria própria (`stems/categorias/`), com a mesma cadeia de mixagem do episódio, para medir a água isolada por seção.
2. Cada cena ficou com **uma gravação de água principal** e só as camadas necessárias.
3. As reduções foram feitas **nas próprias camadas**, cena a cena, e não pelo ducking. A mixagem refinada usa os **mesmos ganhos absolutos de stem** da anterior: tirar camadas reduz de fato o som, sem que os outros efeitos subam para compensar.

**Água por seção (LUFS, mesma escala do mix final):**

| Seção | Antes | Depois | Diferença | O que mudou |
|---|---|---|---|---|
| Abertura e navegação (0–15) | −25,5 | −29,3 | **−3,8 dB** | <ul><li>Impacto mantido forte.</li><li>Bolhas em uma camada que some até o leito.</li><li>Mar −5 dB.</li><li>Onda de proa, espuma e esteira agora seguem a distância da câmera. Antes, a onda de proa era fixa e alta: −6 dB, de 9,0 a 13,6 s.</li></ul> |
| Dique (41–49) | −29,1 | −34,2 | **−5,1 dB** | <ul><li>Água principal = os **jatos**, só −1 dB.</li><li>Removida a cama de "água na tubulação", redundante.</li><li>O enchimento fica mais grave e mais calmo conforme o nível sobe.</li></ul> |
| Empuxo subaquático (49–75) | −31,1 | −37,9 | **−6,8 dB** | <ul><li>O ambiente submerso passou de duas camadas para uma, discreta (−5 dB).</li><li>Mergulho e água deslocada −4 a −6 dB.</li></ul> |
| Retomada e experimento (75–95) | −21,8 | −27,3 | **−5,5 dB** | <ul><li>Impactos mantidos.</li><li>A onda de deslocamento do casco, antes fixa e muito alta (−4 dB), agora segue a arfagem real e some quando o casco para.</li><li>Ambiente submerso −6 dB.</li></ul> |
| Carregamento e calado (95–134) | −35,5 | −40,9 | **−5,4 dB** | <ul><li>Água no casco só enquanto o navio afunda com a carga.</li><li>Cais −5 dB.</li></ul> |
| Avaria e inundação (134–155) | −23,8 | −28,6 | **−4,8 dB** | <ul><li>Água principal = o **jato**.</li><li>Removido o "jorro" simultâneo (3140).</li><li>A turbulência do porão só cresce com o nível.</li><li>Golpes de água: de 5 para 3.</li></ul> |
| Conclusão (155–168) | −23,9 | −24,5 | −0,6 dB | <ul><li>O impacto do bloco de 17 m foi mantido forte de propósito; ele domina a seção.</li><li>Em volta dele: submerso −7 dB, mar final −5 dB.</li></ul> |

**Contraste entre ação e calma** (efeitos + ambiências):

| | Antes | Depois | |
|---|---|---|---|
| **Ação** · impacto da conclusão | −16,5 | −17,2 | −0,8 dB |
| Ação · ruptura do casco | −12,8 | −13,9 | −1,1 dB |
| Ação · encaixe da chapa | −12,6 | −14,1 | −1,5 dB |
| Ação · experimento | −16,6 | −18,2 | −1,6 dB |
| Ação · impacto da abertura | −17,4 | −20,1 | −2,7 dB (bolhas redundantes saíram da janela do impacto) |
| Ação · impacto da retomada | −18,6 | −21,6 | −3,1 dB (idem) |
| Ação · jato da avaria | −18,9 | −22,6 | −3,8 dB (pedido: menos excesso na inundação) |
| Ação · pouso do contêiner | −19,8 | −25,2 | −5,4 dB (sem a pancada grave longa) |
| Ação · comporta + jatos | −17,8 | −25,7 | −7,9 dB (ver abaixo) |
| **Calma** · navegação | −25,9 | −31,4 | −5,5 dB |
| Calma · empuxo subaquático | −31,3 | −38,8 | −7,4 dB |
| Calma · calado e marcas | −32,8 | −37,5 | −4,7 dB |
| Calma · plano final | −32,5 | −37,2 | −4,7 dB |

- Valores das ações: pico momentâneo. Valores dos trechos calmos: média.
- Os trechos calmos baixaram mais que as ações: o contraste aumentou.
- **Comporta:** o pico antigo **não vinha da água**. Vinha de um impacto metálico longo (8 s de estrondo grave, com reverberação larga) somado a uma cama industrial alta. Agora há uma batida metálica no instante certo, reforço grave discreto e os jatos como protagonistas. **Se faltar peso, é o primeiro ponto a subir.**

## 2. Efeitos que respondem à animação

| Ação | Como o som responde |
|---|---|
| **Arrasto do bloco** (abertura e retomada) | <ul><li>**Retomada:** segue a **velocidade real** do bloco (curva da cena s08a) e termina quando ele deixa a borda.</li><li>**Abertura:** o plano 1 vem do animatic e **não tem curva exportada**, então usei um perfil de velocidade do próprio plano (cresce com o empurrão e termina no tombo).</li></ul> |
| **Pórtico do estaleiro** | <ul><li>O motor de translação segue a **velocidade e a aceleração** reais do carro: o volume cresce na arrancada e a rotação sobe levemente com a velocidade.</li><li>**Silencia quando o carro para**; antes ficava constante.</li><li>Rodas no trilho só em movimento.</li><li>**Guincho de içamento** novo, seguindo a carga subindo e descendo.</li><li>Rangidos de cabo só nas arrancadas e frenagens fortes da carga (no máximo 4).</li></ul> |
| **Portêineres** | <ul><li>O motor segue o carro e o spreader. Antes ficava em **25% de volume mesmo parado**; agora **para quando o equipamento para**.</li><li>Vizinhos mais distantes, idem.</li><li>Rangidos de cabo só quando o spreader arranca ou freia com carga (no máximo 3, fora dos pousos).</li></ul> |
| **Solda** | <ul><li>Arco só dentro de cada cordão. **Pausas reais** entre os cordões: a cama contínua de solda ao fundo saiu.</li><li>O crepitar segue o brilho do shader (±4 dB), mais falhas curtas aleatórias do arco.</li><li>Os cordões distantes ficam mais baixos e sem agudos.</li></ul> |
| **Contêineres** | <ul><li>Contato metálico no instante do encaixe (0–3 ms) + **vibração curta** da caixa (0,45 s).</li><li>Saiu a pancada grave longa.</li><li>No tempo acelerado, nenhum som por contêiner.</li></ul> |
| **Água** | <ul><li>Respingos no instante do impacto.</li><li>**Bolhas seguem a descida:** velocidade real do bloco na retomada (s08a) e na conclusão (s13); na abertura, somem até o leito.</li><li>O deslocamento do casco no experimento segue a **arfagem real** e diminui até parar, com 3 batidas cada vez mais fracas.</li><li>Água no casco do porto só enquanto o navio afunda.</li></ul> |
| **Inundação** | <ul><li>O jato nasce na entrada da água, mantém-se com o rombo livre e perde força quando ele é coberto.</li><li>O porão enchendo cresce com o nível.</li><li>Reverberação de compartimento de aço contida.</li><li>A tensão grave cai a partir de 150,6 s e some em 154,6 s, junto com a explicação das divisórias.</li></ul> |

## 3. Moderação

| | Antes | Depois |
|---|---|---|
| Usos de gravações | 174 | 149 |
| Camadas de água | 70 | 57 |
| Whoosh / ar | 9 | 7 (só ar físico de quedas + 2 transições: "Meses depois" e entrada da câmera lenta) |
| Graves sintéticos | 15 | 8: 7 impactos (abertura, encaixe, comporta, retomada, casco do experimento, ruptura, conclusão) + o pulso gráfico "peso = empuxo" |
| Sínteses no total | 20 | 13 (empuxo: só 3 formações gráficas, sem som em cada seta) |
| Impacto pesado 783 | 7 usos | 1 (só no encaixe da chapa; divisórias e comporta com outra batida) |
| Reverberação metálica (envios) | 0,5–0,6 | 0,15–0,35 |

- **Repetição que ainda existe:** o rangido de casco (3076) aparece 12 vezes, em trechos diferentes da gravação. É a única gravação real de rangido de casco disponível. Se soar repetida, ela está no mapa de troca.

## 4. Perspectiva e transições

**Distância real câmera → fonte**, lida quadro a quadro das cenas, controla volume e agudos:
- câmera perto: definido;
- câmera longe: mais baixo e sem agudos;
- nos cortes, a mudança leva ~0,3 s.

Sons com perspectiva:
- navio na navegação: máquinas, onda de proa, espuma, esteira e casco passando;
- pórtico do estaleiro: motor, rodas e guincho;
- portêineres: principal e vizinhos.

**Outros ambientes:**
- **Debaixo d'água:** abafado (agudos cortados) e discreto.
- **Interior do casco:** reverberação de aço contida.
- **Mar aberto:** vento e ondas baixos, com espaço.

**Transições:** todas as ambiências entram e saem com fusões de ~1 s que atravessam o corte. Nenhuma surge ou some seca.

## 5. Mixagem e verificações

| Verificação | Anterior | **Refinado** |
|---|---|---|
| Loudness integrado (WAV) | −14,06 LUFS | **−14,03 LUFS** |
| Pico verdadeiro (WAV) | −1,8 dBTP | **−1,8 dBTP** |
| Pico verdadeiro no AAC final | — | a montagem mantém a medição de pico no AAC (meta −1,6, a última deu −2,4) |
| Mono × estéreo | −14,1 / −14,06 | **−14,04 / −14,03** (sem perda) |
| Voz no celular: fala plena ≥ 10 dB acima do fundo | 93,5% | **97,2%** |
| Voz no celular: mediana | 20,0 dB | **22,8 dB** |
| Ducking | máx. 18 dB, ambiência máx. 9 dB | **igual** (moderado) |
| Ducking médio na fala | 9,8 dB | **8,6 dB** (o fundo já é mais baixo, então o ducking trabalha menos) |
| Música | discreta | igual (mesma trilha e mesmo nível) |
| Stems | 4 + grupos | **4 + grupos de troca + categoria água** |

**Sincronia dos impactos** (ataque medido × evento da animação), todos abaixo de 1 quadro (33 ms):

| Evento | Desvio |
|---|---|
| Borda | −5 ms |
| Água (abertura) | −19 ms |
| Leito | +29 ms |
| Encaixe | −12 ms |
| Comporta | +8 ms |
| Retomada | −15 ms |
| Experimento | −3 ms |
| Pousos 1/2/3 | −2/0/−3 ms |
| Ruptura | −2 ms |
| Divisórias | +6 ms |
| Conclusão | −5 ms |

A nova gravação de batida chegou a ficar 42 a 66 ms fora no primeiro teste. O motivo era um resto do golpe anterior dentro da gravação; ela foi recortada na batida real.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `som/som_refinado.py` | direção sonora refinada |
| `som/movimento.py` | câmera, movimento e perspectiva lidos das cenas |
| `audio_ep01_refinado.wav` + `stems/*_refinado.wav` | mix e stems (fora do git: contêm Mixkit; regeneráveis em ~2 min) |
| `som/auditoria_agua.py` · `som/auditoria_agua_{hibrido,refinado}.json` | água por seção |
| `som/acao_calma.py` · `som/contraste_acao_calma.json` | contraste ação × calma |
| `som/sincronia_refinado.json` | sincronia |
| `som/comparativo_refinado_medidas.json` | níveis dos trechos do comparativo |
| `som/fontes_efeitos_refinado.md` · `som/mapa_substituicao_refinado.md` | fontes, licenças e mapa de troca da versão refinada |

## Próximo passo (depois da sua escuta)

1. Ajustes pontuais que você indicar (instante + "mais" ou "menos"). Os pontos mais prováveis:
   - peso da comporta;
   - ambiente do dique e do empuxo, que tiveram os maiores cortes;
   - volume do pouso do contêiner.
2. Montagem completa de 168 s com o som aprovado: `trocar_audio.py`, sem render 3D.
3. Render de 1080 × 1920 só com a sua autorização.
