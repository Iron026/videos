# Ep. 01 · Versão de revisão (540 × 960, 30 fps reais): relatório

| Item | Arquivo |
|---|---|
| Vídeo de revisão integral | `episodio/ep01_revisao.mp4` (171,0 s · 540×960 · 30 fps · 33,6 MB) |
| Validação técnica | `episodio/ep01_revisao.validacao.json` |
| Testes intermediários | `episodio/testes_revisao/*.mp4` + `validacao_testes.md` |
| Folha de contato | `episodio/folha_revisao.jpg` (54 instantes) |
| Versões anteriores preservadas | `ep01_previa_v1.mp4`, `ep01_previa_v2.mp4`, `ep01_previa.mp4` (v3) |

**Render:** Three.js v2 (r170), decupagem v3, GTAO 4, sem MSAA.
- Todos os **5.130 quadros** foram renderizados individualmente, segmento por segmento, em 14 segmentos.
- Nenhum quadro vem da prévia de 10 fps.
- Quadros distintos medidos (`mpdecimate`, área sem legendas): **4.781 de 5.130** (93 %). Os demais são instantes em que câmera e objeto ficam quase parados (marcas do calado, picadeiros, assinatura final). Não há duplicação artificial.

**Não mudou:**
- Narração original (SHA preservado, sem alteração de velocidade).
- Tempos das legendas.
- Duração de 171,0 s.
- Identidade visual, assinatura e mascote.
- Modelos e física aprovados.

## Ajustes pontuais aplicados

| Pedido | O que foi feito | Situação |
|---|---|---|
| **Carga 100–105 s** sem obstrução | Câmeras de pouso acima das pontes de peação, ao lado da baía. Os três contêineres aparecem descendo, aproximando e encaixando | ✅ Resolvido em 100,1–105 s |
| **Empuxo 48–75 s:** respiro com o navio inteiro | Novo plano 63,1–65,8 s: navio inteiro em diorama, com o volume deslocado se enchendo. A ciência das componentes verticais (fundo e bojo) foi mantida | ✅ |
| **Experimento 84–95 s:** contraste | Os dois objetos ocupam o quadro. Rótulos "Mesma massa do navio vazio" × "Navio vazio" separados. Queda simultânea | ✅ |
| **Conclusão 155–159 s** | O bloco maciço cai **ao lado da proa**, em primeiro plano, e afunda; o navio continua flutuando (eco da pergunta inicial) | ✅ |
| Luz da solda | Halo pulsante (raio de 1,2–1,9 m, brilho 4,0) e faíscas | ⚠️ Parcial (ver abaixo) |
| Espuma da proa | Onda de proa reforçada | ⚠️ Melhor, ainda discreta |
| Quilha × picadeiros | Topos amarelos dos picadeiros, corte ilustrativo, a quilha sobe com o nível | ⚠️ Visível, mas fina |
| Close da linha de carga | O corte para o close acontece quando as linhas acendem. Enquadramento corrigido após o teste (disco e TF inteiros) | ✅ |

## Validação técnica (vídeo integral)

| Verificação | Resultado |
|---|---|
| Formato | H.264 540×960, 30,0 fps; AAC 48 kHz estéreo |
| Duração | 171,0 s (< 180 s) |
| Quadros pretos | nenhum |
| Congelamentos ≥ 1,5 s | nenhum |
| Loudness | −14,0 LUFS integrado; pico real −1,6 dBTP |
| Sincronia da narração | +3 ms em 10 s, 85 s e 160 s (correlação com o MP3 original) |

## Validação intermediária (antes do render integral)

Oito testes a 540×960 com 30 fps reais: carga, empuxo, experimento, conclusão, dique, linha de carga, solda e espuma. Os detalhes estão em `testes_revisao/validacao_testes.md`.

Três problemas encontrados nos testes foram corrigidos antes do render integral, e os quadros afetados foram renderizados de novo:
1. Rótulos sobrepostos no experimento.
2. O close da linha de carga cortava o disco e a linha TF.
3. Halo da solda pequeno.

## Custo

| Etapa | Tempo |
|---|---|
| Exportações no Blender (ajustes) | ~10–15 min (estimado) |
| Testes intermediários (~1.000 quadros) | ~35 min (estimado pelo ritmo medido de ~2,0 s/quadro) |
| Render integral (4.079 quadros novos; os quadros dos testes foram reaproveitados) | 2 h 18 min |
| Montagem e validação | ~5 min |

Nenhum serviço pago foi usado. Nenhuma voz foi gerada. Nada foi publicado.

Estimativa para a versão definitiva a 1080×1920, se autorizada: **≈ 9–14 h** de render (4× pixels; não executado).

## Problemas que ainda existem (objetivo)

1. **Plano 42 (97,6–100,1 s):** as pernas do portêiner ainda aparecem em primeiro plano. O plano é de ambientação (antes do 1º pouso) e a ação não fica tampada, mas a leitura é poluída. Correção: câmera ~8 m mais alta ou do lado do mar. Custo: ~75 quadros.
2. **Luz da solda (23,8–25,3 s):** o motor não anima luzes pontuais. O brilho é um halo emissivo e não ilumina as chapas ao redor. Para luz real, seria preciso estender `render2.js`.
3. **Espuma da proa (11–13,4 s):** mais visível que na v3, mas ainda discreta no celular.
4. **Separação quilha × picadeiros (44,6–47 s):** aparece, mas é fina em 540×960. Na versão de 1080 fica mais nítida; pode ser exagerada (a quilha subir antes) se preferir.
5. **Trim de 0,71° pela proa (avaria):** é fisicamente correto, mas sutil no formato vertical. Os rótulos de calado (proa +2,6 m) carregam a informação.
6. **Continuidade da superestrutura:** no estaleiro o navio ainda não tem superestrutura; no corte interno, ela já aparece. O salto é aceitável como elipse, mas pode ser percebido.
7. **Vistas subaquáticas em diorama:** são uma escolha de estilo, porque a câmera não entra na água do motor. A água é shader, sem simulação de fluido; splashes e bolhas são partículas.
8. **Segmento das marcas (s11):** é basicamente o movimento contínuo da v2 com o novo close. Funciona, mas é o trecho menos "cortado".
9. **Hipóteses adotadas (documentadas):**
   - 20 t por contêiner.
   - GM₀ = 1,5 m.
   - Duplo fundo de 2,2 m e tanques laterais de 2,0 m estanques.
   - μ = 0,95 no porão.
10. **Resolução de revisão:** detalhes finos (algarismos das marcas, setas pequenas) só ficam totalmente nítidos na versão de 1080×1920.
11. **Pontos de escuta da narração** (validação anterior): por exemplo, "ganha (a) forma". Continuam para conferência humana; a narração não foi alterada.

**Próximo passo:** aguardando sua avaliação. A versão definitiva a 1080×1920 não foi renderizada.
