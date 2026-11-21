# Ep. 02 · Relatório da rodada 1 (auditoria → pré-produção → implementação → animatic)

**Nada publicado.** Nenhuma voz gerada, nenhum crédito da ElevenLabs gasto, nenhum serviço contratado. O Ep. 01 não foi
alterado. Render em 1080 × 1920 **não iniciado**.

## 1. Auditoria do Ep. 01 (Fase 1)

| Componente | Situação | Uso no Ep. 02 |
|---|---|---|
| `blender/lib.py`, `ep_base.py`, `exportar_rt2.py` | Genéricos (materiais, câmera por chaves, exportação por segmento) | Fork em `blender/` (procedência em `motor/PROCEDENCIA.md`) |
| `motores/tempo_real_v2/render2.js` | Genérico, com partes específicas do navio (água, espuma, alagamento) | Fork `motor/render3.js` + recursos novos |
| `episodio/montar_ep01.py` | Lista de segmentos e assinatura específicas do navio | Reescrito como `montar_ep02.py` (mesma lógica de fusões, rótulos, legendas e loudness) |
| `episodio/render_final.py` | Padrão de checkpoints e manifesto | Base para `render_planos.py` (o definitivo herdará o manifesto completo) |
| `grade_ep01.py`, `detectar_cintilacao.py` | Genéricos | Copiados sem mudança |
| `som/som_refinado.py`, `movimento.py` | Arquitetura reaproveitável; fontes e eventos do navio | Entram depois da narração aprovada (`som/plano_som.md`) |
| `navio.py`, `cenario.py`, `hidro.py`, `ep01_cenas.py` | Específicos do navio | Não reaproveitados |

**Limitações do ambiente encontradas e tratadas:**
- Contêiner novo, sem `bpy`, Three.js ou scipy: tudo foi reinstalado (bpy 5.1.2, three 0.170.0 fixado no `package.json`).
- Não há GPU: o renderizador por software leva ~10 s para iniciar cada plano e ~1,5 s por quadro em 270 × 480.
- Modelos do Whisper: rede liberada no ambiente, mas o download foi **negado pela permissão da sessão** (ver §4).

## 2. Ciência (Fase 2)

- Modelo didático com propriedades reais do R600a (CoolProp): `ciencia/validacao_cientifica.md`.
- **10 de 10 testes científicos passam:**
  - sentido de circulação, fases e continuidade;
  - sucção só com vapor;
  - condensação com rejeição de calor;
  - expansão isentálpica;
  - calor do quente para o frio;
  - 1ª lei (Q̇_rej = Q̇_abs + Ẇ, resíduo 0,000 W);
  - COP < Carnot;
  - lados de pressão.
- Um teste falhou na primeira versão. A causa não era erro do modelo, e sim física real: o líquido aquece **16 mK** no
  início do capilar (Joule–Thomson negativo de líquidos). Corrigi o critério do teste, não os dados.
- **Compressor:**
  - biela-manivela exata, com curso de 16,0 mm e espaço morto de 0,80 mm, verificados;
  - a sucção abre a 56° e a descarga a 324°;
  - o vapor aquece de −10 para 15 °C dentro da carcaça hermética. Essa temperatura foi **calculada** para fechar com os 72,7 °C de
    descarga do modelo do ciclo.
- Roteiro revisado: **nenhum erro científico**. Há duas observações para a imagem, sem mudar o texto
  ("bruscamente" = queda distribuída no capilar; nenhuma energia entra ou sai no capilar).

## 3. Implementação (Fase 3)

- **Modelo:** geladeira de uma porta com:
  - paredes isoladas;
  - congelador/evaporador em U;
  - serpentina traseira com arames;
  - compressor hermético com mecanismo interno;
  - filtro secador e capilar enrolado;
  - cozinha com janela.
- **Circuito contínuo de 22 m.** Os testes de cena passam (continuidade, ciclo fechado, folga ≥ 3 mm entre tubos e sem
  invasão do compressor). Os testes acharam **um defeito real antes de qualquer render**: a linha de descarga atravessava
  as curvas da serpentina (−5,2 mm de folga). Corrigido, agora com 16,8 mm.
- **Motor `render3.js`:**
  - visão térmica com varredura;
  - fluido no tubo, com duas escalas de detalhe e antisserrilhado contra cintilação;
  - feixes de calor;
  - pulsos de trabalho;
  - dois planos de corte com tampa colorida;
  - curvas de animação.
- **Decupagem como dados:** 39 planos ancorados em palavras. Trocar a narração recalcula tudo. Isso já foi usado nesta
  rodada, quando a narração recebida substituiu a estimativa.

### Defeitos encontrados na revisão visual e corrigidos

| Defeito | Causa | Correção |
|---|---|---|
| Porta de armário dentro da geladeira | O laço criava 6 portas onde cabem 5 | 5 portas de 43,8 cm |
| Sol ao contrário | Rotação do sol errada | Sol entrando pela janela |
| Visão térmica igual à imagem normal | O ambiente era cinza-claro | O ambiente virou cinza-ardósia |
| A4 confuso | — | Tela dividida frente × traseira |
| B2 com a placa do evaporador de lado | Câmera na altura exata da placa | Câmera reposicionada |
| B3 com a porta tapando a lateral | — | Câmera frontal-esquerda alta |
| "Sombras" azuis dos feixes | A oclusão de ambiente incluía os feixes transparentes | Feixes no passo transparente, com profundidade que respeita o corte e ignora o vidro |
| Porta cortada antes da hora em C1 | — | Corte só a partir do início da varredura |
| C3 sem leitura do fluido | — | Close num passe do condensador |
| D2 e início de H1 todos amarelos | Câmera dentro da espuma do teto | Câmeras reposicionadas |
| C4, E4, F2 e G3 com a vista bloqueada ou o objeto perdido | — | Câmeras reposicionadas |

## 4. Narração aprovada
Ver `voz/validacao_narracao.md` e `roteiro/palavras_meta.json`.

- Aprovada pelo usuário; texto colado conferido **idêntico** ao roteiro oficial (389 palavras). MP3 original preservado
  (somente leitura, SHA-256 registrado). Duração da fala 149,9 s; episódio **151,2 s** (fala + 1,6 s de respiro).
- **Estrutura confere:** 37/37 fins de frase caem em pausas, em ordem (resíduo médio 0,43 s).
- **Palavras ainda não verificadas** uma a uma (sem Whisper). Os cortes usam o início das frases, que é o dado confiável;
  as legendas palavra a palavra podem estar algumas centenas de ms deslocadas dentro da frase.
- Duração abaixo da meta de 2:40–2:55 do prompt: a meta dizia "respeitando a duração efetiva da narração aprovada";
  não estiquei nada.

## 4b. Animatic (Fase 4)
- Arquivo: `episodio/ep02_animatic.mp4` · 540 × 960 (render 270 × 480 ampliado), 30 qps, 151,23 s, 24,7 MB,
  SHA-256 `50a12881ae4593775a8bea7311c46d9d3eb52cbc2c8cc3aab3d45b116d911d4c`.
- 41 planos renderizados (39 + metades das telas divididas A4b e J1b), um processo por vez, 22:10 → 23:21.
  **Verificação de quadros: 0 ruins** (tamanho mínimo e não-preto). Montagem: 4.537 quadros, 5 min.
- Áudio: só a narração aprovada (sem efeitos). −16,4 LUFS integrados (normalização de prévia; a meta −14 LUFS e o
  pico verdadeiro ≤ −1,5 dBTP medidos no AAC ficam para a mixagem).
- Selo "ANIMATIC · não publicar" em todos os quadros. Folha de contato do meio de cada plano:
  `relatorios/contato_animatic_v1.jpg`.

### Defeitos que eu mesmo encontrei no animatic (ainda NÃO corrigidos)
| Plano | Instante | O que se vê | Causa provável | Correção proposta |
|---|---|---|---|---|
| A3 | 3,5–5,0 s | Quase o plano todo é uma parede cinza; a serpentina só aparece no fim | A órbita da câmera passa rente à lateral do gabinete | Órbita mais aberta, serpentina visível desde o início |
| B2 e J2 | 12,5–14,5 s · 139–141,5 s | Planos brancos/cinza sem leitura: não dá para ver o congelador "sem névoa" | Câmera perto demais da caixa do congelador, olhando a face inferior | Plano médio com o congelador e a prateleira no quadro |
| B7 | 26–28,5 s | Tudo azul; os feixes estão lá, mas o evaporador não é reconhecível | Enquadramento fechado demais na visão térmica | Abrir para mostrar a caixa do congelador recebendo os feixes |
| D4 (e início de D5) | 64–69 s | Macro do canal ocupa pouco do quadro; a evaporação (bolhas → vapor) não se lê | Câmera longe para um "macro"; tubo fino | Aproximar e alinhar o canal na diagonal do quadro |
| G3 | 102–106 s | Um pote vermelho da prateleira tapa metade do quadro no meio do plano | Objeto do interior entre a câmera e o capilar | Ocultar o objeto nesse plano ou mover a câmera |
| H1 | 106–108 s | Início escuro e sem referência | Começo dentro do vão do congelador | Começar já fora, no evaporador |

Planos revisados nesta rodada e que **resolveram** o problema anterior: A4/J1 (tela dividida), B3, C1, C3, C4, D2, E4, F2.
(Medido pela folha de contato; a aprovação visual é sua.)

## 5. O que esta rodada NÃO tem (de propósito)
- **Som:** só narração. Efeitos entram depois que você aprovar a estrutura (`som/plano_som.md`).
- **Polimento de luz e material:** a imagem ainda é "limpa e diagramática". O polimento vem depois que estrutura e câmeras
  forem aprovadas, para não render duas vezes.
- **Prévia em 540 e render final.**

## 6. Limites honestos
- Eu não assisto nem escuto como uma pessoa. As folhas de contato e as medições acham erros, mas não aprovam a estética.
- O animatic tem 270 × 480 a 15 quadros/s, ampliado. Serve para ritmo, câmera e ordem dos conceitos, não para qualidade
  de imagem.
