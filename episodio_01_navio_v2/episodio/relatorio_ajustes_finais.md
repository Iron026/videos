# Ep. 01 · Ajustes finais de direção: relatório

| Entrega | Arquivo |
|---|---|
| Montagem curta (só os trechos corrigidos, 61,6 s) | `episodio/ep01_ajustes_finais_trechos.mp4` |
| Comparativo antes/depois (lado a lado, mesmo áudio, 61,6 s) | `episodio/comparativo_ajustes_finais.mp4` |
| Folha antes/depois (17 instantes) | `episodio/comparativo_ajustes_finais.jpg` |
| Versão completa atualizada (montagem dos quadros existentes, sem render integral) | `episodio/ep01_revisao_ajustes.mp4` + `.validacao.json` |
| Versão anterior preservada | `episodio/ep01_revisao.mp4` (os quadros antigos ficam em `quadros_revisao_antes/`) |

**Render:** só os quadros alterados, a 540 × 960 com 30 fps reais (Three.js v2, GTAO 4).
- **1.610 quadros em 70,75 min.**
- Os outros 3.520 quadros da versão de revisão foram reaproveitados. Conferi que a câmera e os objetos deles são idênticos aos da exportação anterior.
- Não houve render integral nem benchmark.

## O que mudou (só enquadramento; física e tempos intactos)

| Trecho | Antes | Depois |
|---|---|---|
| **1 · Empuxo**<br>planos 28–29 (56,6–62,9 s) | Seção frontal a ~55 m: faixa estreita no meio do quadro, céu e água vazios | 3/4 elevado, quase frontal: a seção fica maior, e o convés e a superestrutura preenchem o topo. O plano 28 abre um pouco mais para as setas laterais (que se anulam) ficarem inteiras |
| **1 · Empuxo**<br>planos 31–32 (65,8–74,9 s) | Seção frontal pequena | 3/4 rente à linha d'água: o volume deslocado (ciano), as setas e o casco ocupam a maior parte do quadro |
| **2 · Experimento**<br>83,85–94,55 s | Os dois objetos pequenos, numa faixa no terço superior | Um só movimento em 3/4, elevado e próximo. Os objetos aparecem grandes, e o casco mostra o comprimento (o "volume muito maior"). A câmera acompanha a **queda simultânea**: o bloco afunda e o casco para no calado de equilíbrio. Seguem o close frontal do ar interno e a síntese em 3/4 (água deslocada, empuxo = peso) |
| **3 · Guindaste**<br>97,6–100,1 s | Pernas do portêiner em primeiro plano | Câmera no convés do navio: o contêiner sobe no cais e vem sobre o navio contra o céu, com o portêiner ao fundo |
| **4 · Marcas**<br>125–134 s | Algarismos do calado minúsculos; "10M/11M" cortados pela curvatura da proa; disco da linha de carga cortado na borda | Close a ~3 m: algarismos de calado nítidos no celular. O texto foi afastado do casco e "9M/10M" aparecem inteiros. A linha de carga inteira (disco e TF…W) fica no quadro, com o rótulo acima, sem cobrir as letras |
| **5 · Conclusão**<br>154,6–166,3 s | Bloco cortado e chapado; plano final de perto, sem o navio inteiro | ver os 5 tempos abaixo |

**Os 5 tempos da conclusão:**

| Tempo | O que se vê |
|---|---|
| ① 154,6–155,2 s | Bloco de aço **em primeiro plano**, grande, com o navio carregado atrás |
| ② 155,2–158,7 s | O bloco cai e **afunda** (a câmera desce com ele) enquanto o navio **continua flutuando** |
| ③ 158,7–162,4 s | **Revelação** da parte submersa ao longo do casco; o volume deslocado acende, com o ciano mais nítido |
| ④ 162,4–164,35 s | **Peso = empuxo** com setas grandes |
| ⑤ 164,35–166,3 s | **Aérea 3/4 do navio inteiro** no mar contínuo, antes da assinatura |

O bloco e o navio na mesma imagem respondem à pergunta da abertura.

**Detalhes técnicos dos ajustes:**
- No experimento, o espaço entre o bloco e o casco passou de 7 m para 5 m, só para o par caber melhor no quadro vertical. Massa, aresta (17,2 m), tempos de queda, calado e amortecimento não mudaram.
- Na conclusão, o volume deslocado ficou mais opaco (alfa 0,52) para ler ciano sobre a pintura vermelha do casco, e não lilás.
- No plano final da conclusão, o mar passa a ser contínuo, sem o corte do diorama. Assim não aparece o fundo da caixa de água.

## Validação

**Testes de enquadramento:** antes do render, cada ajuste passou por quadros-teste a 270 × 480 (cerca de 20 variantes de câmera). Os escolhidos depois foram renderizados a 540 × 960 com 30 fps reais.

**Problemas encontrados e corrigidos na conferência:**
1. Bloco tocando a borda esquerda no experimento: o enquadramento foi deslocado.
2. Disco da linha de carga cortado: recentralizado.
3. Rótulos "Marca de linha de carga" (cobria TF/W) e "Marcas de calado" (cobria um algarismo): reposicionados. Os rótulos são desenhados na montagem, então não foi preciso renderizar de novo.

**Validação técnica da versão completa atualizada (`ep01_revisao_ajustes.mp4`):**

| Item | Resultado |
|---|---|
| Formato | 540 × 960, 30,0 fps, 5.130 quadros, 171,0 s |
| Quadros distintos | 4.784 (antes: 4.781) |
| Quadros pretos / congelamentos ≥ 1,5 s | nenhum / nenhum |
| Loudness | −14,0 LUFS, pico −1,6 dBTP |
| Sincronia da narração | +3 ms em 10, 85 e 160 s |

Narração original, legendas, trilha, efeitos e duração: inalterados.

## O que ainda pode ser notado

1. **Água em diorama:** nos planos submersos ainda há uma faixa de água lisa abaixo da quilha (empuxo e conclusão, ~25–35% do quadro). É inerente ao corte da água sem objetos extras. Não acrescentei elementos para preenchê-la, como pedido.
2. **Experimento em perspectiva:** em 3/4, o bloco (mais perto da câmera) parece grande em relação ao casco. O rótulo "Mesma massa do navio vazio" e o casco se estendendo para trás mantêm a leitura correta (mesma massa, volumes muito diferentes).
3. **Plano do guindaste:** a estrutura do portêiner continua presente como fundo e moldura (é um portêiner real), mas não tampa mais a ação.
4. **Itens já relatados que não foram objeto desta rodada:**
   - halo da solda;
   - espuma da proa;
   - trim de 0,71°.

**Próximo passo:** aguardando sua aprovação destes ajustes. Depois dela, o render definitivo a 1080 × 1920 (≈ 9–14 h) pode ser autorizado. Nada foi publicado e nenhum serviço foi contratado.
