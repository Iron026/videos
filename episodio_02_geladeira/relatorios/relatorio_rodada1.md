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

## 4. Narração recebida
Ver `voz/validacao_narracao.md`.

- Arquivo preservado com SHA-256. Duração de 149,9 s, com voz ~10 % mais rápida que no Ep. 01.
- **Estrutura confere** com o roteiro: os 37 fins de frase caem em pausas, em ordem.
- **Palavras não verificadas.** O animatic usa estes tempos com o selo "narração não verificada".

## 5. O que esta rodada NÃO tem (de propósito)
- **Som:** entra depois da narração aprovada.
- **Polimento de luz e material:** a imagem ainda é "limpa e diagramática". O polimento vem depois que estrutura e câmeras
  forem aprovadas, para não render duas vezes.
- **Prévia em 540 e render final.**

## 6. Limites honestos
- Eu não assisto nem escuto como uma pessoa. As folhas de contato e as medições acham erros, mas não aprovam a estética.
- O animatic tem 270 × 480 a 15 quadros/s, ampliado. Serve para ritmo, câmera e ordem dos conceitos, não para qualidade
  de imagem.
