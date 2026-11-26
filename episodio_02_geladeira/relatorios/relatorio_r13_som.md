# Ep. 02 · R13: revisão do sound design (TESTE para sua aprovação)

O definitivo R12 continua **congelado**. Esta rodada não mexeu em imagem, animação, câmeras, legendas, garrafa, transição C, modelo científico nem encerramento, e não houve render 3D.

Os comparativos usam **os quadros do definitivo R12 sem alteração**: só o áudio muda. Cada trecho vem precedido de uma cartela que diz qual versão toca.

Eu meço, mas não escuto: **a aprovação auditiva é sua.** **Nada foi publicado.**

## Para você ouvir (em `episodio/previas_r13/`)

| Arquivo | O que mostra |
|---|---|
| `01_ruido_isolado.mp4` | **O ruído contínuo isolado**, no nível exato da R12, sem voz, música e efeitos: (1) as duas camadas juntas na abertura; (2) só o tom de cômodo; (3) só o zumbido do compressor; (4) as duas a +12 dB, só para você reconhecer o caráter |
| `02_ab_ruido.mp4` | A = R12 como entregue × B = **R12 sem o ruído contínuo** (o resto é idêntico à R12) |
| `03_ab_musica.mp4` | A = música da R12 × B = **nova presença musical** × C = opção "música +3 dB". As três sobre a mesma base (efeitos da R12, sem ruído) |
| `04_ab_efeitos.mp4` | A = efeitos da R12 × B = **efeitos revisados**, sobre a mesma música nova e sem ruído |
| `05_previa_combinada.mp4` | A = R12 × B = **teste R13 completo** em 8 momentos: abertura, revelação do circuito, evaporador, compressor, condensador, capilar, retirada do leite e encerramento |

## 1. O ruído contínuo

### Origem

Testei cada stem separadamente, sem presumir. Para isso, decompus a mixagem V9, que é a base de R10–R12, em uma camada por fonte; a soma das camadas reproduz os stems aprovados com nulo de −150 a −169 dBFS.

O ruído vem de **duas camadas presentes o episódio inteiro**:

| Camada | Fonte | Presença | Nível | Caráter |
|---|---|---|---|---|
| **Tom de cômodo** | Freesound 329568, "Room Tone Apartment Small Bachelor" | **100 %** do tempo, inclusive dentro do circuito em corte | **−37 LUFS constante** | ar de fundo, com **tom de 120 Hz** (+26 dB acima da vizinhança) |
| **Zumbido do compressor** | Freesound 455776, gravado de perto | **100 %** do tempo ("ligado o episódio todo") | −30 LUFS no conjunto; **−21 LUFS no E3**, −24 a −26 no G1–G2 | zumbido de **120 Hz** (+40 dB) e 50 Hz |

O que **não** é a origem:
- **A narração:** é limpa, com piso de −85 a −89 dBFS. Não apliquei nenhuma redução de ruído na voz.
- **O gorgolejo** (só nos planos D) e **o chiado do capilar** (só no G3) são localizados.

Na abertura e nos últimos 21 s, o tom de cômodo era o único som além da voz, porque ali não havia música, e por isso ficava exposto. Nos planos internos (C a G), quem dominava era o zumbido do compressor.

### Correção

| Camada | O que mudou |
|---|---|
| **Tom de cômodo** | **removido**. A abertura agora tem só voz, porta e passos: silêncio ambiental natural. |
| **Compressor** | O mesmo som e a mesma perspectiva de distância da R12, mas **só quando faz sentido** (ver abaixo) |

O compressor toca:
- **A3/A4:** quando a câmera mostra a traseira, discreto e abafado pelo gabinete;
- **E2:** **liga no instante em que o trabalho elétrico chega ao compressor** (75,37 s, com o clique do relé);
- **E3:** em câmera lenta, "pesando" a cada compressão do pistão;
- **E4:** some quando a câmera segue a descarga;
- **I2:** **sobe** quando ele "precisa trabalhar mais" com a porta aberta, a mesma curva da animação, ×1 → ×2,2;
- **J4:** cai a zero junto com o trabalho na imagem.

Resultado: a camada contínua estava presente 100 % do tempo; agora está presente **15 %**, só nesses trechos.

## 2. A música quase inaudível

### Por que estava baixa

Na fala, a música ficava **21,4 LU abaixo da voz**, e **24,6 dB abaixo** na faixa do celular. As causas são medidas:

1. O nível de base era calibrado **antes** do abaixamento: 13,5 LU abaixo da voz.
2. **O abaixamento de −8 dB ficava ligado em praticamente toda a narração**, porque ela quase não tem pausas.
3. Havia um corte fixo de −3 dB em 0,9–3,2 kHz.
4. A faixa já é escura: só 2,4 % da energia está acima de 1 kHz, justamente a região que o celular reproduz melhor.
5. As duas camadas de ruído ficavam **no mesmo nível da música** e a mascaravam.
6. A faixa **acaba aos 124 s**: os últimos 21 s do episódio, o encerramento, não tinham música.

### O que mudou

- **Duração:** a faixa foi estendida **9 compassos** (93,97 BPM, compasso de 2,554 s) com duas emendas no tempo forte. Os pontos foram escolhidos pela maior semelhança espectral (8 compassos + 1).
  - O acorde final agora cai aos **149,76 s, logo depois de "calor."**, a última palavra.
  - O trecho calmo da faixa passa a acompanhar a conclusão.
  - **Ouça as emendas em 1:43,6 e 2:04,0.**
- **Sem corte fixo.** O abaixamento passou a ser **dinâmico e só na banda da voz** (250 Hz–4 kHz): a cada instante de fala, a música fica ≥ 16 dB abaixo da voz nessa banda, enquanto graves e agudos seguem.
- O abaixamento segura 0,5 s depois da fala, para não cobrir o final das palavras.
- **Automação de contexto:**

| Momento | Ajuste |
|---|---|
| transição C | +3 dB |
| revelação do circuito | +2,5 dB |
| ida ao evaporador | +2 dB |
| "E tudo recomeça" | +2,5 dB |
| acorde final | +3 dB |
| pausas reais (≥ 0,6 s) | +1,5 dB |
| explicação densa, E3 e G3 (onde os mecanismos falam) | −1,5 a −2,5 dB |

A narração deste episódio tem **só 10 pausas de 0,6 s ou mais**, somando 6,6 s, a maior de 0,75 s. Por isso a presença da música não pode depender só das pausas: ela teve de subir também por baixo da fala.

### Resultado

| Medida | R12 | Teste R13 |
|---|---|---|
| Música − voz durante a fala (LUFS momentâneo) | −21,4 LU | **−16,0 LU** |
| Música durante transições e revelações | −35,4 LUFS | **−28,9 LUFS** (+6,5 dB) |
| Música no encerramento (129,6–151 s) | **ausente** | **−32,6 LUFS** |
| Música presente durante a fala | 83 % | **97 %** |
| Música − voz na faixa do celular, durante a fala | −24,6 dB | −23,7 dB |

**Limite honesto:** num **alto-falante de celular, durante a fala contínua**, a música ganhou pouco (+0,9 dB). Ali o critério já aprovado de voz dominante (voz ≥ 10 dB acima do resto no p5) não deixa ir mais longe. Onde ela ganha de verdade:
- em fone e caixa (corpo e graves);
- nas transições e revelações;
- no encerramento;
- e por não estar mais mascarada pelo ruído.

Se você quiser mais música, a opção **C, "+3 dB"**, no `03_ab_musica.mp4`, fica 13 LU abaixo da voz. Ela **reprova** o critério da voz no celular (p5 de 8,0 dB): é uma escolha sua.

## 3. Efeitos: removidos, substituídos, adicionados

O critério foi o seu: efeito só onde há ação, movimento que leva a outro lugar ou revelação, **nunca em corte comum**. Mais contraste: o impacto mais forte fica na revelação do circuito; a explicação contínua tem poucos efeitos.

| Situação | Som | Onde | Por quê |
|---|---|---|---|
| **Removido** | tom de cômodo (329568) | episódio inteiro | era a camada contínua de ruído |
| **Restringido** | zumbido do compressor (455776) | só A3/A4, E2–E4, I2, J4 | o som só existe quando o compressor é mostrado ou citado |
| **Substituído** | pop das apresentações (776443) → **pop de vídeo explicativo** (Mixkit 3005) | fluido, evaporador, compressor, condensador, capilar | mais definido. O **pico** cai no primeiro quadro do rótulo (±0 ms) |
| **Substituído** | chiado sintetizado do capilar → **chiado real de gás em tubo fino** (Freesound 453443) | G3, começa em "parte" (104,3 s) | é o fenômeno físico real: a expansão ao sair do capilar |
| **Melhorado** | válvulas do E3 (relé filtrado, −53 LUFS, inaudível) → **toque metálico curto** (Mixkit 2857, pré-clique cortado) | 7 aberturas no E3 | nos instantes da animação; nível constante |
| **Adicionado** | **relé de partida** (876593) | E2, 75,37 s | o trabalho elétrico liga o compressor |
| **Adicionado** | **pistão** (Freesound 669468, 0,8×) + o zumbido "pesando" | E3, nos 4 fins de compressão (78,69 · 79,96 · 81,19 · 82,46 s) | mecanismo visível em câmera lenta. *Representação didática* |
| **Adicionado** | **transição C** (Mixkit 166 + 175), da direita para a esquerda | 5,74 s | é o único corte com movimento (empurrão de 0,3 s) |
| **Adicionado** | **impacto discreto** (Freesound 754424) | **na pausa** depois de "não fabrica frio." (14,44 s) | primeira revelação conceitual |
| **Adicionado** | sopro do calor transportado (Mixkit 1474) | B3 | o feixe contorna a parede |
| **Adicionado** | **revelação do circuito**: aproximação (Mixkit 2615) + **impacto principal** (Freesound 754422) + sopro do pulso (Mixkit 1474) | C2: 34,33 s (o circuito surge) e 34,74–37,86 s (o pulso dá a volta) | maior revelação do episódio. O pulso é *representação didática* |
| **Adicionado** | fluido no tubo (Freesound 553257, abafado) | C3 | o fluido circulando. *Representação discreta* |
| **Adicionado** | 3 movimentos de câmera (Mixkit 2608, 1474, 1489) | C4 → D1 (47,73 s) · E1 (72,77 s) · H1 (109,88 s) | só deslocamentos que levam a outro ponto do circuito |
| **Mantidos** | porta, passos, mão no puxador, caixa de leite, prateleira de vidro e pouso da garrafa, gorgolejo do evaporador | como na R12 | já adequados. O gorgolejo agora fica só em D1–D5, mais presente quando as bolhas crescem (D4) |

### Sincronia

Medida no som isolado em relação ao instante da ação na cena:

| Tipo | Desvio do pico |
|---|---|
| Pops, válvulas, relé, impactos | **0 a ±9 ms** (um quadro tem 33 ms) |
| Pistão | ataque 17 ms antes, pico 1 ms antes do fim da compressão |
| Whooshes | crescem antes, de propósito, e chegam ao pico no movimento (±2 ms) |

Nenhum efeito continua depois que a ação acaba, e os sons de mecanismo saem quando o plano troca.

## 4. Validação técnica do teste R13, medida no AAC

| Medida | Teste R13 | R12 | Meta |
|---|---|---|---|
| Loudness | **−14,13 LUFS** | −14,09 | −14 |
| Pico verdadeiro | **−1,60 dBTP** | −1,52 | ≤ −1,5 |
| Voz − resto no celular (p5 / mediana / pior janela) | **10,5 / 22,7 / −4,1 dB** | 10,3 / 23,3 / −8,7 | p5 ≥ 10 |
| Perda em mono | −0,03 dB | −0,02 | ~0 |
| Último 0,5 s | **−47,7 dBFS** | −45,6 | silêncio |
| Efeitos sobre a fala: voz − resto na janela de cada evento | **6,9 a 23 dB** (30 eventos) | — | ≥ 6 dB |
| AAC × WAV em cada evento | correlação ≥ 0,997, atraso 0 | — | ≥ 0,98 |

- A pior janela de voz − resto melhorou de −8,7 para −4,1 dB.
- O ponto fraco da R12 em 1:44 ("…bruscamente, *e* parte") passou de −8,7 para −2,5 dB.
- O chiado do capilar começa em "parte", e não na pausa antes do "e".

**Métrica técnica não é aprovação.** Esses números mostram que a voz continua dominante e que o arquivo está dentro das metas. Se a experiência ficou melhor, só a sua escuta diz.

## 5. O que não mudou

- **Voz:** o mesmo stem da R12, amostra a amostra. O MP3 original está intacto e os tempos das palavras não mudaram.
- **Duração:** 151,233 s.
- **Imagem:** nenhum quadro mudou; os comparativos usam o vídeo R12.
- **Efeitos mantidos:** porta, passos, mão, leite, prateleira e garrafa são os mesmos sinais da R12.
  - Fora das janelas dos 5 pops, o stem desses efeitos é **idêntico bit a bit** (−300 dBFS) ao da R12.
  - Porta, passos e gorgolejo vêm da decomposição provada da V9.
- **Trilha:** continua Spice Intrigue.
- **Definitivo R12:** intacto em `episodio/definitivo_r12/`.

## 6. Limites e pendências

1. **Não escutei** nada disto: as escolhas de som foram feitas por medição (duração, ataque, centroide, grave, nível) e por título. A sua escuta decide.
2. **Canal de referência:** usei as suas diretrizes e os títulos públicos do Desmontando o Mundo. A ferramenta para baixar os vídeos e analisar o áudio deles foi **bloqueada pela política de permissões desta sessão**, e não contornei. Se quiser essa análise, ela precisa da sua autorização.
3. **Emendas da música:** ouça em **1:43,6** e **2:04,0**.
4. **Licenças:** ver `relatorios/licencas_r13.md`.
   - Narração: plano gratuito da ElevenLabs, **sem uso comercial**.
   - Música: Pixabay; a conferência da página fica com você.
   - Efeitos novos: Freesound CC0 e Mixkit, ambos sem atribuição exigida.
5. **Contêiner temporário:** os WAV e stems ficam fora do git, mas são regeneráveis por `som/som_r13.py`. Os comparativos e os registros estão no git.

## 7. Depois da sua aprovação

O definitivo R13 **não exige render**: é a troca do áudio sobre os masters de imagem da R12 (`ffmpeg … -c:v copy`), seguida das validações no AAC final. Só faço isso depois do seu ok, incluindo a escolha entre B e C na música e eventuais ajustes que você pedir.

**Nada foi publicado.**
