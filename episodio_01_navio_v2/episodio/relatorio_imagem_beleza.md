# Ep. 01 · Piso do porão corrigido e imagem mais bonita no episódio inteiro

| Entrega | Arquivo |
|---|---|
| **Revisão completa nova** (168 s, 540 × 960, 30 fps) | `episodio/ep01_revisao_visual.mp4` |
| **Comparativo lado a lado** (antes = revisão aprovada · depois = nova) | `episodio/ep01_comparativo_visual_beleza.mp4` (25 s) |
| Master de imagem sem legendas, atualizado (para trocar o áudio sem refazer a imagem) | `episodio/ep01_master_imagem_sem_legendas.mp4` |

**Trechos do comparativo:**
1. Porão da avaria
2. Divisórias
3. Solda
4. Navegação
5. Porto
6. Plano final

Som, narração, legendas e tempos são **os mesmos** da revisão aprovada. Por isso a trilha é a do som anterior: o som refinado e as buzinas ainda aguardam a sua escuta e entram depois pelo master (`trocar_audio.py`, ~75 s).

## 1. O "piso bugado" do porão

- **Causa:** o navio é mostrado **cortado ao meio** (corte ilustrativo). O sol entrava pelo lado aberto e projetava no piso e nas paredes do porão sombras de baixa resolução, serrilhadas e azuladas: as "faixas" e "dentes" no fundo.
- **Por que estava errado:** num porão fechado essa luz não existe.
- **Correção:** o interior do porão (piso, paredes, tanques, anteparas e estrutura) **não recebe sol direto**. Ficou com um cinza de primer uniforme.
- **Estrutura de navio real**, para o porão não parecer uma caixa lisa:
  - cavernas a cada 3 m nas paredes;
  - longarina horizontal no costado;
  - reforços verticais na parede do tanque lateral;
  - três longarinas no fundo duplo, que aparecem através da água.
- **Água:** é a versão nova já entregue (água do mar com profundidade, jato aerado, espuma, bolhas, linha do nível).

## 2. Imagem mais bonita no episódio inteiro

| Melhoria | Efeito |
|---|---|
| **Qualidade final de render**: antisserrilhado 4× (antes: nenhum) e oclusão ambiente de 16 amostras (antes: 4) | bordas limpas (proa, cabos, guarda-corpos), menos moiré nas ondulações dos contêineres, sombreamento de contato mais suave |
| **Bloom sutil** (limiar alto) | halo só nas luzes fortes: arco e faíscas da solda, reflexos do sol, linhas luminosas; o resto da imagem não muda |
| **Correção de cor** (só na imagem 3D, antes de rótulos e legendas) | <ul><li>Curva em S leve e saturação +5 %.</li><li>Sombras levemente frias e altas luzes levemente quentes.</li><li>Vinheta suave (−10 % nas bordas).</li><li>Unifica os planos sem mudar o caráter.</li><li>Cores da marca, rótulos e legendas não são afetados.</li></ul> |

- **Render:** todos os **5.148 quadros** do episódio foram renderizados de novo, ~4h15, sem erros. A contagem é idêntica à da revisão anterior em todos os segmentos.
- **Revisão anterior:** os quadros estão guardados em `quadros_revisao_antes6/`.

**Limites honestos:**
- O porão ficou mais claro do que antes, porque agora não há sombras do sol. Se preferir um interior mais escuro e dramático, é um ajuste de cor rápido.
- O bloom é deliberadamente discreto.

## 3. Verificações

| Item | Resultado |
|---|---|
| Duração | 168,000 s · 5.040 quadros · 30 fps |
| Decodificação | sem erros |
| Quadros pretos / trechos parados | 0 / 0 |
| Loudness / pico (AAC final) | −14,0 LUFS / −2,4 dBTP |
| Sincronia da narração | +3 ms, constante |
| Física, enquadramentos, rótulos, tempos | inalterados |

Nada foi publicado. O render de 1080 × 1920 não foi iniciado. O perfil final já usa a mesma qualidade de antisserrilhado e oclusão; o bloom entra com `bloom=0.22`.

> ⚠️ A narração segue do plano gratuito da ElevenLabs. O episódio **não está licenciado para exploração comercial** (`voz/LICENCA_NARRACAO.md`).
