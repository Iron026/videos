# Ep. 01 · Validação científica e hipóteses de cálculo (prévia v2)

Todos os números saem de `blender/hidro.py`, que integra numericamente a mesma forma de casco usada na modelagem (`navio.meia_boca`), com água salgada ρ = 1,025 t/m³. Os resultados da avaria ficam em `episodio/hidro_avaria.json`.

## 1. Hidrostática do casco (verificada)

| Calado T | Volume deslocado | Deslocamento | KB | Área de flutuação |
|---|---|---|---|---|
| 8,0 m (navio vazio, leve) | 38.690 m³ | 39.657 t | 4,19 m | 5.382 m² |
| 9,42 m (carregado) | 46.456 m³ | 47.617 t | 4,95 m | 5.524 m² |
| 10,0 m (verão, marca S) | 49.655 m³ | 50.897 t | 5,25 m | 5.574 m² |

O volume a 8,0 m confere com o valor de referência do projeto (38.689 m³).

## 2. Dique seco

- O casco vazio está apoiado nos picadeiros, com a quilha a 1,6 m do piso do dique.
- A água entra pela comporta e sobe. Enquanto a profundidade sobre a quilha é menor que 8,0 m, o empuxo é menor que o peso e o casco continua apoiado.
- Com 8,0 m de profundidade sobre a quilha, empuxo e peso se igualam (39.657 t) e o casco **deixa os picadeiros**.
- Daí em diante o casco **acompanha o nível**, com calado constante de 8,0 m. Na cena, a linha d'água fica parada na marca **8M** enquanto o dique continua enchendo (em 48,0 s o nível já está 1,9 m acima do ponto de flutuação).
- A cena não tem oscilação nem afundamento depois de flutuar, porque não há força que os produza: o enchimento é quase estático.
- O enchimento real leva horas. A cena é um time-lapse, sinalizado com "Tempo acelerado".

## 3. Pressão e empuxo

| Item | Representação |
|---|---|
| Setas de pressão | 6 setas, todas perpendiculares ao casco: 2 rasas e 2 fundas nos costados, 2 no fundo. Comprimento ∝ profundidade (p = ρ·g·h); a cor também escurece com a profundidade |
| Pares laterais | Iguais e opostos: "se compensam" e somem |
| Resultante | Só sobra a componente vertical. As setas do fundo convergem para a linha de centro e viram o **empuxo**, aplicado em B (KB = 4,19 m) |
| Princípio de Arquimedes | O volume deslocado (ciano) é exatamente o volume do casco abaixo da linha d'água. O empuxo usa a mesma família de cor ("empuxo = peso da água deslocada"). O peso do navio é aplicado em G, igual e oposto, na mesma vertical |

## 4. Bloco × casco

| Comparação | Valores |
|---|---|
| Bloco pequeno (abertura) | Aço com aresta de 1,6 m. Empuxo / peso = ρ_água / ρ_aço = 1.025 / 7.850 = **0,13** |
| Bloco grande (comparação) | **Mesma massa do navio vazio**: 39.657 t ÷ 7,85 t/m³ = 5.052 m³, aresta de **17,2 m**. Desloca só o próprio volume, empuxo = 13% do peso: afunda |
| Casco | Mesmo peso, mas desloca 38.690 m³, porque o interior é ar: empuxo = peso, flutua |

O rótulo "Mesma massa do navio vazio" e a escala (17 m ao lado do casco) evitam confundir o bloco grande com o bloco de 1,6 m da abertura.

## 5. Carregamento, calado e marcas

**Carregamento**
- 398 contêineres de 40 pés, com **massa média adotada de 20 t** (7.960 t no total).
- Calado de 8,00 → **9,42 m**.
- Cada lote do time-lapse (~57 contêineres) afunda ~0,2 m, o mesmo espaçamento dos algarismos da escala de calado.
- A arfagem amortecida mostra o peso crescendo antes e o empuxo alcançando-o até o novo equilíbrio.

**Escala de calado:** padrão métrico. Algarismos de 10 cm a cada 20 cm, com a base do algarismo no calado indicado e os metros inteiros com "M". Fonte refeita (a anterior confundia 9 e 0).

**Marca de linha de carga:** proporções reais.

| Elemento | Medida |
|---|---|
| Anel | Ø 300 mm, traço de 25 mm |
| Linha horizontal | 450 mm |
| Linhas de carga | 230 mm, a 540 mm a vante |
| S (verão) | Centro do disco, 10,0 m |
| T e W | S ± T/48 = ± 0,208 m |
| F e TF | Acima de S e de T pela tolerância de água doce FWA = Δ/(4·TPC) = **0,22 m** (TPC = 57,1 t/cm), para ré |

Escala de calado (proa) e marca de linha de carga (meia-nau) aparecem separadas, cada uma com seu rótulo.

## 6. Avaria e compartimentação

**Hipóteses** (documentadas no código):

| Hipótese | Valor adotado |
|---|---|
| Duplo fundo | 2,2 m de altura, **estanque**, não alagado |
| Tanques laterais | 2,0 m de largura, do fundo interno até z = 6,0 m, **estanques**, não alagados. Acima deles o porão é limitado pelo costado simples |
| Rombo | No costado simples, a z = 7,4 m (abaixo da linha d'água de 9,42 m). Só o **porão** x = 10,0–37,2 m (entre duas anteparas transversais estanques) se comunica com o mar |
| Permeabilidade | Porão vazio μ = 0,95 |
| Método | Perda de flutuabilidade. O porão aberto ao mar deixa de contribuir com volume **e** com área e inércia de flutuação; isso é o efeito de superfície livre de um compartimento em livre comunicação com o mar. KG não muda |
| Estabilidade intacta | KG adotado de 12,18 m, o que dá GM intacto carregado de **1,50 m** (valor típico de porta-contêineres) |

**Resultado** (equilíbrio de volume e de centro longitudinal resolvido numericamente):

| Grandeza | Antes | Depois |
|---|---|---|
| Calado a meia-nau | 9,42 m | **10,69 m** (+1,27 m) |
| Trim | 0 | **0,71° pela proa** |
| Calado na proa | 9,42 m | 11,98 m |
| Calado na popa | 9,42 m | 9,46 m |
| Borda livre na proa | — | **6,0 m** (o navio continua flutuando) |
| GM | 1,50 m | **0,74 m**: queda pelo efeito de superfície livre do porão alagado, ainda positivo. Como o porão é simétrico, não há banda |

**Nota sobre o trim:** a primeira correção estimava 0,65° considerando tanques laterais de altura total. Nessa geometria, porém, qualquer rombo no costado atingiria primeiro um tanque lateral, o que não é coerente com tanques estanques preservados. Com a estrutura acima (tanques baixos e costado simples), o rombo alaga só o porão e o resultado consistente é **0,71°**, ainda dentro do "aproximadamente 0,65°" pedido. Não foi criada avaria lateral.

**Na cena**
- A água entra pelo rombo (jato) e sobe até o nível do mar lá fora, com a superfície sempre horizontal (contra-rotação do trim).
- A **linha d'água anterior**, pintada no navio, desce e se inclina em relação ao **nível do mar** tracejado.
- Os rótulos "Proa: +2,6 m" e "Popa: +0,0 m" quantificam o trim.
- A hipótese grave ("sem divisórias") aparece porão a porão em vermelho e é desfeita antes de "divisórias estanques", que são destacadas nas duas anteparas que contêm a água.
- O enchimento é acelerado ("Tempo acelerado").

## 7. Continuidade

- **Abertura (4,4–15,1 s):** é **outro** porta-contêineres (casco cinza e verde, chaminé verde, 5 camadas de carga). Ilustra "olha este gigante… carregando milhares de toneladas".
- **Navio do episódio:** vazio do estaleiro até 94,55 s, porque os segmentos 03–08b têm 0 contêineres (contagem nos arquivos exportados). Recebe a carga a partir de 100,1 s ("Um guindaste traz o primeiro") e mantém os mesmos 398 contêineres e o calado de 9,42 m nos segmentos 10–13.
