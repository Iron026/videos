# Ep. 01 · Prévia dinâmica v3: relatório de direção

| Item | Arquivo |
|---|---|
| Prévia integral | `episodio/ep01_previa.mp4` (171,0 s; render 270×480 a 10 fps, montagem a 540×960 / 30 fps) |
| Versões anteriores preservadas | `ep01_previa_v1.mp4`, `ep01_previa_v2.mp4` |
| Decupagem | `episodio/decupagem_ep01_v3.md`: 66 planos, cada um com fala, objetivo, ação, câmera, transição, modelos e necessidade de render |
| Comparativo | `episodio/comparativo_previa_v2_v3.jpg`: 24 instantes que eram os mais estáticos da v2, com v2 acima e v3 abaixo |
| Trechos a 30 fps | `episodio/trechos_30fps/` (render a 30 fps reais, 270×480 ampliado; ver abaixo) |

**O que não mudou:** a narração (intacta), as legendas (mesmos tempos das palavras), a assinatura, a duração (171,0 s) e a física corrigida da v2.

## O que mudou: acontecimentos, não só câmera

| Trecho | v2 | v3 |
|---|---|---|
| 4–15 s · gigante | 1 plano contínuo, navio parado | 5 planos com o navio **navegando a 6 m/s**: geral de escala com esteira → pilhas de contêineres → travelling contrário ao longo do costado → proa avançando com a onda de proa → o navio se afasta |
| 15–30 s · estaleiro | 4 planos | 8 planos: aérea → **carro do pórtico e cabos** (contra-plongée) → chapa descendo → encaixe → **macro da solda** → laterais chegando → proa chegando → geral |
| 30–41 s · corte | 1 movimento contínuo | 5 planos: casco pronto → **proa se afasta** (acompanhada de lado) → células acendendo em sequência → **dentro do porão** (contra-plongée com operários) → ar seco e recuo |
| 41–48 s · dique | 2 planos | 4 planos: comporta com jatos → rente à água subindo pelos picadeiros → **corte ilustrativo** (a parede próxima some por 2,4 s) mostrando a quilha **se afastar dos picadeiros** e subir com o nível → marca 8M |
| 48–75 s · empuxo | Seção quase fixa | 8 descobertas: **mergulho** → **mapa de pressão no casco 3D** (cor ∝ profundidade) → câmera desce pelo costado com as setas crescendo → pares horizontais se anulam e **o bojo fica só com a componente vertical** → **todas as componentes verticais (fundo e bojo) se somam** no empuxo → o volume submerso **se enche de ciano** → peso da água deslocada = empuxo → peso do navio = empuxo |
| 75–84 s · bloco | 1 plano | 4 planos: geral → close das forças → cubo de água deslocada ao lado → **do leito**: impacto com **nuvem de sedimento** |
| 84–95 s · experimento | Lado a lado estático | **Experimento:** bloco de 17,2 m (mesma massa do navio vazio) e casco **suspensos**, **soltos juntos**: splash duplo; o bloco mergulha e some, o casco afunda até 8 m e **para**, com arfagem amortecida. Depois o ar interno, o volume deslocado e empuxo = peso |
| 95–117 s · carga | Planos parecidos | 8 planos: aérea → portêiner erguendo do caminhão → **close do pouso** → 2º e 3º pousos → descida até a linha d'água → **vista zenital do convés enchendo** → barras de peso e empuxo |
| 117–124 s · calado | 1 plano | 3 planos; a câmera **acompanha a ponta da cota** da quilha à superfície |
| 134–155 s · avaria | Corte desde o início | Novo plano **exterior**: o rombo abaixo da linha d'água e **bolhas sugadas** para dentro. Depois **interior** (jato), nível subindo na parede, porão cheio, navio inteiro (calado e trim), hipótese, **close das anteparas** e geral |
| 155–166 s · conclusão | Navio + setas | **O bloco maciço cai ao lado e afunda** enquanto o navio flutua → volume deslocado sob o casco → peso = empuxo e recuo |

**Correção didática importante (48–62 s):** na v2, só as setas do fundo formavam o empuxo, o que sugeria que ele vem só da pressão no fundo. Agora as componentes verticais do **bojo também** entram na soma, e os costados (só horizontais) se anulam. Fica correto que o empuxo é a resultante da pressão em **toda** a superfície molhada.

**Áudio:** novos efeitos para cada acontecimento (máquinas e onda de proa, guincho, mergulho, mapa de pressão, convergência, enchimento do volume, splash duplo do experimento, sedimento, rombo e gorgolejo, bloco final). A narração e a trilha original não mudaram.

## Medições

| Medida | v2 | v3 |
|---|---|---|
| Planos detectados automaticamente (`scene` > 0,28) | 16 | **37** |
| Planos na decupagem | ~20 | **66** |
| Maior trecho sem corte detectado | 75 s | 19,7 s* |

\* O detector conta como um plano só uma sequência de planos diferentes da **mesma** cena com cores parecidas (por exemplo, a seção do empuxo, 56,6–76 s, que na v3 tem 5 planos distintos). Por isso fica abaixo dos 66 planos da decupagem.

**Validação técnica**

| Item | Resultado |
|---|---|
| Duração | 171,0 s |
| Sincronia da narração | +3 ms nos três pontos medidos |
| Loudness | −14,0 LUFS, pico −1,6 dBTP |
| Quadros pretos / congelamentos | nenhum / nenhum |

**Física preservada:**
- **Dique seco:** flutua com 8,0 m e acompanha o nível.
- **Avaria:** +1,27 m, 0,71°, GM 0,74 m.
- **Bloco:** E/P = 0,13; o bloco de mesma massa tem 17,2 m de aresta.
- **Carga:** calado com 398 contêineres = 9,42 m.
- **Queda no experimento:** queda livre até a água, depois ~7,9 m/s² descendo. O casco afunda até o calado de equilíbrio com amortecimento.

## Trechos a 30 fps (fluidez real)

| Arquivo | Trecho |
|---|---|
| `ep01_v3_30fps_dique.mp4` | 41,55–48,0 s: dique seco, corte ilustrativo |
| `ep01_v3_30fps_empuxo.mp4` | 48,0–63,0 s: mergulho, pressão, componentes, empuxo |
| `ep01_v3_30fps_experimento.mp4` | 83,85–94,55 s: bloco × casco soltos juntos |
| `ep01_v3_30fps_avaria.mp4` | 134,0–146,0 s: exterior, interior, nível subindo |

## Custo desta rodada

- Exportações no Blender: ~15 min.
- Prévia dos 12 segmentos alterados: 1.525 quadros em **~21 min**.
- Trechos a 30 fps: ~1.330 quadros, ~18 min.
- Montagens: ~2 min cada.
- Nenhum render de revisão nem definitivo foi executado.
- Próximos passos, se autorizados: revisão a 540×960 ≈ 4 h; final a 1080×1920 ≈ 11–17 h.

## Cenas que ainda precisam de refinamento

1. **Pouso do 1º contêiner (100,1–101,9 s) e "E mais outro" (103–104,9 s):** as estruturas do portêiner ainda tampam parte da ação. O contêiner pousando precisa de um enquadramento mais limpo (por exemplo, de cima do convés vizinho).
2. **Retomada do bloco na conclusão (155–158,7 s):** o bloco cai longe da câmera e fica pequeno; aproximar ou trazer para o lado do casco.
3. **Macro da solda (23,8–25,3 s):** legível, mas abstrato; faltam brilho e luz da solda (o motor não anima luzes pontuais).
4. **Seção do empuxo (48–75 s):** agora tem 8 planos, mas é a mesma cena por 27 s. Vale considerar um respiro intermediário (por exemplo, o plano 3D do navio inteiro em 63–66 s).
5. **Onda de proa (11–13,4 s):** a espuma fica tênue na água; reforçar.
6. **Dique (44,6–47,0 s):** a separação quilha × picadeiros aparece, mas é fina na resolução da prévia; conferir no render de revisão.
7. **Marcas (123,65–134 s):** segmento mantido da v2 (movimento motivado contínuo de ~10 s). Pode ganhar um corte para close do disco quando as linhas acendem.
8. **Resolução:** as prévias a 270×480 escondem detalhes finos (algarismos, setas pequenas). Fluidez e legibilidade definitivas só no render de revisão.
