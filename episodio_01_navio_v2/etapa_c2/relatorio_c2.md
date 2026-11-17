# Episódio 01: revisão final de composição (v3c)

Renderizado no **Three.js v2**, com as otimizações aprovadas (GTAO com 8 amostras, MSAA 4×), em 1080×1920. Cada quadro levou de 7,3 a 9,4 s nesta máquina sem GPU. Nenhum benchmark novo foi necessário.
Os arquivos anteriores foram preservados (`etapa_b/`, `etapa_c0/`, `etapa_c1/`). **O animatic não foi iniciado e nada foi publicado.**

| Quadro | Arquivo |
|---|---|
| 2 · Estaleiro | `etapa_c2/quadros/quadro2_v3c.png` |
| 3 · Interior do casco | `etapa_c2/quadros/quadro3_v3c.png` |
| 4 · Empuxo | `etapa_c2/quadros/quadro4_v3c.png` |

## Quadro 2: estaleiro
- **Menos céu e menos chão:** o pórtico foi rebaixado de 60 para 46 m. A câmera foi aproximada e escolhida por busca numérica, com a proa na metade esquerda e a viga perto do topo; o casco e o guindaste agora dominam o quadro.
- **Bulbo de proa:** saiu a esfera esticada. Entrou uma forma fusiforme, com seção superelíptica mais alta que larga, corpo embutido no casco e nariz elíptico projetado cerca de 8 m à frente da roda de proa.
- **Cabos ligados fisicamente à peça:**
  - dois olhais (amarelos), com manilhas, soldados na borda superior do painel;
  - as lingas saem do anel do gancho e terminam exatamente nos olhais;
  - o gancho fica na vertical do centro de massa calculado do painel, como numa peça suspensa em equilíbrio.
- **Preservados:** estaleiro, operários, chapas e a ação de montagem (o painel desce para o vão do costado).

## Quadro 3: interior do casco
- **Preservado:** porão aberto e vazio, sem contêineres.
- **Nível externo da água:** a linha amarela sólida virou um **tracejado claro** que atravessa a seção, com o rótulo **"Nível da água lá fora"**. O piso do porão fica cerca de 7 m abaixo desse nível e continua seco.
- **Interior seco porque o casco é estanque:** o chapeamento externo aparece em amarelo, como um **contorno contínuo e fino** em toda a seção (costado, bojo e fundo), com o rótulo **"Casco fechado e estanque"**.
- **Aço fino × grande volume:** esse contorno, junto com o duplo fundo e os tanques laterais em células, mostra o pouco aço que envolve o grande volume de ar do porão.
- **Água profunda:** o leito, as pedras e a areia saíram. O mar escurece com a profundidade, do azul-esverdeado perto da superfície para o azul-marinho. O efeito vem do espalhamento e da absorção no shader da água.

## Quadro 4: empuxo
- **Menos setas:** de 18 para 10 setas de pressão (por bordo: 2 no costado, 1 no bojo a 45° e 2 no fundo).
- **Física preservada:** cada seta é perpendicular ao casco, aponta para ele e tem comprimento proporcional à profundidade. A soma sobre a seção continua dando zero na horizontal e a área submersa na vertical, como verificado na revisão anterior.
- **Peso aplicado em G e empuxo aplicado em B:**

  | Ponto | Altura acima da quilha | Origem |
  |---|---|---|
  | **B** (centro de carena) | 4,72 m | Calculado com a forma real do casco para 9 m de calado |
  | **G** (centro de gravidade) | 12,5 m | **Estimativa didática** para porta-contêineres carregado (KG ≈ 0,7 × pontal); o peso real da carga não foi modelado |

  - As duas setas têm **o mesmo tamanho, sentidos opostos e a mesma linha de ação vertical**, marcada por um tracejado.
  - Pontos e rótulos: **"Peso (G)"** e **"Empuxo (B)"**.
  - B fica dentro do volume deslocado (ciano): o empuxo nasce do volume de água deslocado, não do fundo do mar.
- **Sem apoio no fundo:** o leito foi removido e a água é profunda, então o navio aparece flutuando.

### Observação técnica
O motor em tempo real ganhou três recursos usados aqui:
- rótulos na identidade da marca, ancorados em pontos 3D;
- linhas tracejadas;
- destaque do chapeamento externo na face de corte.

Também corrigi um erro de exportação (metadados aninhados eram salvos como texto) e um erro de ordem (rótulos projetados antes de posicionar a câmera).

## Narração
A tentativa única autorizada foi feita depois de confirmar o saldo: plano gratuito, 0 de 10.000 créditos usados, sem excedente, custo estimado de 204 créditos.
- **A geração começou e foi recusada pela ElevenLabs:** *"Unusual activity has been detected on your account, so Free Tier access has been disabled. This can be triggered by using a proxy or VPN…"*.
- **Nada foi cobrado:** o saldo continua em 0 usados.
- **Não fiz novas tentativas,** como você instruiu.

Detalhes e caminhos possíveis estão em `voz/estado.md`.

**Aguardo a aprovação dos três quadros e uma decisão sobre a voz antes de avançar.**
