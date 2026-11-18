# Validação intermediária: testes em 540 × 960, 30 fps reais

**Qualidade de revisão:** Three.js v2, GTAO 4, sem MSAA, cada quadro renderizado (nada duplicado da prévia de 10 fps). Os quadros desses testes ficam em `quadros_revisao/` e são reaproveitados no render integral.

| Teste | Trecho | Quadros | Distintos* | Resultado |
|---|---|---|---|---|
| `teste_carga.mp4` | 99,6–105,0 s | 162 | 154 | Os três contêineres **aparecem descendo e encaixando** (câmera acima das pontes de peação, ao lado da baía). O plano de 97,6–100,1 s ainda tem as pernas do portêiner em primeiro plano |
| `teste_empuxo.mp4` | 59,6–68,0 s | 252 | 248 | Componentes verticais (fundo e bojo) convergem → empuxo → **respiro com o navio inteiro** (o volume deslocado se enche) → volta à seção. Leitura imediata |
| `teste_experimento.mp4` | 84,0–89,0 s | 150 | 138 | Os dois objetos enchem o quadro; queda e contraste claros. **Corrigido depois do teste:** os rótulos "Mesma massa do navio vazio" e "Navio vazio" se sobrepunham |
| `teste_conclusao.mp4` | 155,0–158,7 s | 111 | 111 | O bloco maciço cai **ao lado da proa**, em primeiro plano, e afunda; o navio continua flutuando |
| `teste_dique.mp4` | 44,5–47,5 s | 90 | 82 | No corte ilustrativo, os topos amarelos dos picadeiros marcam a separação; a quilha se afasta e sobe com o nível |
| `teste_linha_carga.mp4` | 129,5–133,5 s | 120 | 97 | O close motivado deixa letras e linhas legíveis no celular. **Corrigido depois do teste:** no fim, o close cortava o disco e a linha TF |
| `teste_solda.mp4` | 23,8–25,3 s | 45 | 43 | Faíscas visíveis. **Corrigido depois do teste:** o halo da solda estava pequeno (agora raio de 1,2–1,9 m e mais brilho) |
| `teste_espuma.mp4` | 11,0–13,35 s | 70 | 70 | A onda de proa ficou mais visível que na v3, ainda discreta |

\* Quadros distintos (`mpdecimate`, área da imagem sem legendas): os quadros repetidos aparecem só onde a câmera está quase parada sobre um objeto parado (marca de linha de carga, picadeiros). Não há quadro duplicado por render.

**Verificações:**
- **Legendas e rótulos** legíveis a 540 × 960. Os rótulos ficam acima de 60% da altura e não colidem com as legendas.
- **Continuidade** entre os planos testados: sem saltos de posição.
- **Colisões ou artefatos:** nenhum encontrado nos trechos testados.
