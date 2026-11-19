# Ep. 01 · Sound design, mixagem e encerramento: relatório

| Entrega | Arquivo |
|---|---|
| Versão integral atualizada (168,0 s, 540 × 960, 30 fps) | `episodio/ep01_revisao_som.mp4` + `.validacao.json` |
| Destaques do som (7 sequências, 83,6 s) | `episodio/ep01_som_destaques.mp4` |
| Gráfico de loudness por stem | `episodio/som_loudness_ep01.png` |
| Stems separados (FLAC 24 bits, 48 kHz) | `episodio/stems/ep01_{narracao,efeitos,ambiencias,musica}.flac` |
| Medições da mixagem e lista de efeitos | `episodio/som/mix_ep01.json` |
| Código | `som/eventos_som.py` (eventos tirados das cenas) · `som/sintese.py` (síntese) · `som/som_ep01.py` (roteiro sonoro, stems, mixagem) |

**Animação:** nada foi re-renderizado além dos 110 quadros do plano final (que agora termina antes). Todos os outros quadros são os da versão aprovada.

## 1. Encerramento e retomada

- **Fim natural:** sem mascote, título, slogan ou escurecimento.
  - O último movimento da câmera foi reajustado para **concluir em 168,0 s**, 1,9 s depois da última palavra científica ("…todo o peso do navio.", 166,12 s). Não há prolongamento além disso.
  - Os rótulos "Empuxo"/"Água deslocada" somem antes do corte para a aérea.
- **Áudio do fim:** a fala de assinatura (166,56–169,86 s) foi retirada **só da cópia de montagem**; o corte fica em 166,36 s. **O MP3 original não foi alterado** (SHA 79e1e8f2…).
  - A música resolve em Ré sob a última palavra.
  - Música, mar e efeitos descem juntos de −21 dB (166,0 s) ao silêncio (168,0 s).
  - Não há sino nem vinheta.
- **Retomada (1:15):** saíram o chip "Retomando o experimento" e o rótulo "O mesmo bloco do início". O bloco é reconhecido pela continuidade (o mesmo cais, o mesmo bloco, o mesmo enquadramento e o mesmo som de atrito da abertura). Fica só o chip "Câmera lenta", que é aviso de tempo, como no resto do episódio.

## 2. Como o som foi feito

- **Fontes:** 100% síntese original neste projeto, sem amostras de terceiros, música protegida ou serviços contratados:
  - **impactos metálicos:** síntese modal (modos inarmônicos do aço);
  - **água:** respingos em camadas e bolhas pelo modelo físico de Minnaert (frequência ∝ 1/raio);
  - **atrito:** grânulos de atrito por *stick-slip*;
  - **máquinas:** motores harmônicos que seguem a velocidade;
  - **ambiente:** reverberações sintéticas por ambiente.
- **Sincronização pelos eventos reais da animação** (`eventos_som.json`, extraído dos arquivos de cena):

  | Evento | Fonte do tempo |
  |---|---|
  | Contêineres | 395 instantes de pouso + 3 pousos dos portêineres |
  | Chapas | 39 chegadas |
  | Faíscas | 184 nascimentos |
  | Motores | velocidade quadro a quadro dos carros, spreaders e guinchos |
  | Arfagem do casco | instantes de inversão |
  | Abertura | tempos físicos (empurrão, borda, água, leito) |

- **Ambientes diferenciados**, cada um com sua reverberação:

  | Ambiente | Uso no episódio |
  |---|---|
  | Externo | mar e vento |
  | Industrial | estaleiro, reverberação longa |
  | Porto | — |
  | Dique | concreto |
  | Interno | compartimento de aço, com modos graves |
  | Subaquático | abafado: o que a câmera vê debaixo d'água soa filtrado |

## 3. Efeitos acrescentados por sequência

| Sequência | Efeitos |
|---|---|
| **0:00–0:15** · bloco e navio | <ul><li>Atrito do aço no concreto (0,5–1,4 s).</li><li>Raspão e baque grave quando o bloco tomba na borda.</li><li>Queda em câmera lenta.</li><li>**Impacto pesado na água em câmera lenta**: baque, lençol d'água, colapso da cavidade, gotas.</li><li>Bolhas e água deslocada ouvidas debaixo d'água.</li><li>Impacto abafado no leito com sedimento.</li><li>Mar e vento.</li><li>Diesel distante.</li><li>Apito grave distante.</li><li>Massa do costado passando.</li><li>**Onda de proa** e borrifo.</li><li>Esteira se afastando.</li></ul> |
| **0:15–0:41** · estaleiro e construção | <ul><li>Motor do carro do pórtico (acelera e freia com o movimento real).</li><li>Guincho com catraca e tambor.</li><li>Cabos cantando sob tensão.</li><li>Rangidos dos cabos a cada arrancada/freada.</li><li>Rangidos sutis da estrutura.</li><li>**Encaixe pesado da chapa** com vibração estrutural.</li><li>**Solda:** arco com zumbido elétrico e crepitação, modulado pela **mesma tremulação luminosa do shader** (por quadro).</li><li>**Um estalo para cada uma das 184 faíscas**, no quadro em que nasce.</li><li>39 contatos das chapas que chegam ao casco.</li><li>Pancadas industriais distantes.</li><li>Reverberação de grande espaço industrial.</li><li>Separação pesada da proa.</li><li>Brilho sutil das células (sem bipe).</li><li>Estalo térmico no porão vazio.</li></ul> |
| **0:41–0:48** · dique | <ul><li>Baque grave da comporta/válvulas e sopro de pressão.</li><li>Jatos fortes.</li><li>Enchimento cada vez mais grave e profundo.</li><li>Água alcançando o casco.</li><li>**Alívio estrutural discreto** quando o peso deixa os picadeiros (sem colisão nem ruptura).</li><li>Água livre ao redor do casco flutuando.</li></ul> |
| **0:48–1:15** · pressão e empuxo | <ul><li>Entrada da câmera na água: respingo e bolhas; o mundo fica abafado.</li><li>**Um único som** para o grupo de setas de pressão: o casco sob pressão (não um som por seta).</li><li>Pulsos graves dos dois lados que empurram.</li><li>Sopro que converge ao centro quando as laterais se anulam.</li><li>Ar subindo na convergência das verticais.</li><li>Impulso grave quando o empuxo se forma.</li><li>Água deslocada quando o volume se enche.</li><li>Pulsos graves de equilíbrio.</li></ul> |
| **1:15–1:35** · bloco × casco | <ul><li>O **mesmo atrito** do cais, em outra variação.</li><li>Borda e queda.</li><li>Impacto na água coerente com a abertura, **com camadas diferentes** (não é cópia).</li><li>Transição suave para a câmera lenta.</li><li>Bolhas grandes e lentas.</li><li>Impacto no leito e sedimento abafado.</li><li>Experimento: **entrada do bloco** (compacta, pesada) e **do casco** (larga, grande massa d'água), em lados opostos do estéreo.</li><li>Onda de deslocamento.</li><li>Água batendo no casco a cada inversão da arfagem (5 vezes, cada vez mais fraca).</li></ul> |
| **1:35–2:14** · carregamento e calado | <ul><li>Motores, guinchos e cabos dos 3 portêineres, seguindo a velocidade real.</li><li>**Pouso de cada contêiner no instante exato do contato** (101,60 · 102,95 · 104,45 s): baque, cantos e trepidação.</li><li>**395 contatos no time-lapse**, cada um no seu instante.</li><li>Água se movendo conforme o calado aumenta.</li><li>Porto ao fundo, com pancadas distantes.</li><li>Marulho no casco.</li><li>Marcas: só toques muito discretos.</li></ul> |
| **2:14–2:35** · avaria e inundação | <ul><li>**Ruptura metálica localizada**.</li><li>Bolhas sugadas pelo rombo.</li><li>**Jato sob pressão** que diminui quando é coberto.</li><li>Porão enchendo: turbulência grave crescente.</li><li>9 golpes de água nas estruturas internas.</li><li>6 rangidos do casco sob carga crescente.</li><li>Reverberação de compartimento de aço.</li><li>Tensão grave crescente até a hipótese grave; depois **alivia gradualmente** a partir das divisórias estanques (baque firme e calmo).</li><li>Sem explosões nem estalos sem representação visual.</li></ul> |
| **2:35–fim** · conclusão | <ul><li>Entrada enorme do bloco de 17 m, em camadas.</li><li>Massa de água deslocada.</li><li>Bolhas e descida abafadas.</li><li>Volume sob o casco.</li><li>Pulso de equilíbrio.</li><li>Mar natural no plano final.</li><li>Música resolvendo.</li><li>Fim suave.</li></ul> |

## 4. Mixagem e validação

| Requisito | Resultado |
|---|---|
| Loudness integrado | **−14,1 LUFS** (arquivo final AAC) |
| Pico verdadeiro | **−1,8 dBTP** (≤ −1,5) |
| Limitador | atua no máximo 2,8 dB, só em transientes de impacto (sem compressão contínua) |
| Duração / sincronia | **168,0 s** · narração **+3 ms** em 10, 85 e 160 s · sem quadros pretos nem congelamentos |
| Voz principal + ducking dinâmico | <ul><li>Sobre a **soma** de efeitos, ambiências e música: na banda da fala (200 Hz–5 kHz) o fundo fica ≥ 13 dB abaixo da voz.</li><li>Graves −6 dB e agudos meio-caminho durante a fala.</li><li>Ataque de 10 ms e liberação de 450 ms (sem "bombear" entre palavras).</li><li>Média de −10 dB durante a fala.</li><li>Nas pausas, os impactos voltam inteiros.</li></ul> |
| Graves | todos os stems sem conteúdo abaixo de 35 Hz; graves dos efeitos baixados sob a voz |
| Mono | <ul><li>Mix mono −14,06 LUFS × estéreo −14,03 LUFS (medido no mix antes do AAC): sem perda por cancelamento.</li><li>Correlação L/R 0,98.</li><li>Nenhum atraso entre canais: a largura vem de ruídos independentes e reverberações descorrelacionadas.</li></ul> |
| Alto-falante de celular (simulação mono, 350 Hz–7 kHz) | <ul><li>Voz **22,7 dB** acima do resto (mediana).</li><li>Em **95,4%** das janelas de fala plena, a voz fica ≥ 10 dB acima do fundo.</li><li>Percentil 5: 10,2 dB.</li></ul> |
| Dinâmica entre cenas | LRA 2,4 LU (típico de conteúdo narrado). Os efeitos variam de quase silêncio (marcas, empuxo) a picos fortes (impactos, avaria), como mostra o gráfico |
| Stems | 4 stems separados e alinhados ao vídeo: a mixagem pode ser refeita sem renderizar o 3D. O script regenera tudo em ~2 min |

**Onde a voz ainda fica abaixo de 10 dB (5% das janelas):** no início ou fim de palavras e no instante exato de alguns contatos (pousos dos contêineres, ruptura e jato da avaria), por menos de 0,2 s cada.

## 5. Limitações (objetivas)

1. **Não escutei a mixagem:** avaliei com medições objetivas (loudness, pico, mono, celular, voz × fundo, sincronia). A escuta em fones e no celular é necessária para julgar o *timbre* dos efeitos.
2. **Efeitos sintetizados:** são coerentes e sincronizados, mas podem soar menos "gravados" que uma biblioteca profissional de foley. Os stems e o arquivo de eventos permitem substituir qualquer efeito por uma amostra licenciada no mesmo instante, sem mexer na animação.
3. **Ducking:** em trechos de efeito contínuo e forte sob fala contínua (jato da inundação) ele chega a −24 dB. É perceptível como um recuo do jato quando a voz fala, o que é intencional.

**Próximo passo:** aguardando sua aprovação. O render definitivo a 1080 × 1920 não foi iniciado e nada foi publicado.
