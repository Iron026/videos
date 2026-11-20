# Ep. 01 · Vazamento do mar no experimento casco × bloco (s08b, ~86–90,5 s)

**Entregas**

| Entrega | Arquivo |
|---|---|
| Revisão integral atualizada | `episodio/ep01_revisao_s08b_corrigido.mp4` |
| Comparativo (trecho lado a lado + 3 detalhes ampliados do fundo duplo, 16 s) | `episodio/ep01_comparativo_s08b.mp4` |
| Detalhe em imagem | `ep01_s08b_detalhe.jpg` |
| Validação quadro a quadro | `validacao_s08b_quadros.json` |

**Base preservada:** a revisão aprovada `ep01_revisao_seis_ajustes.mp4` e os quadros anteriores do segmento (`quadros_revisao_antes8/s08b`).

## 1. Investigação

Os mesmos quadros do s08b foram renderizados em três variantes:
- oclusor antigo (`ocl=1`), que reproduz os quadros entregues, com diferença média 0,19–0,26 de 255;
- oclusor corrigido;
- cena sem a água do mar.

**Resultados:**
- **É o mesmo conflito de profundidade da avaria.** Nos pixels em que a correção muda a imagem, o resultado fica praticamente igual ao da cena sem mar: diferença 1,3–3,7, contra 9,6–19,2 da versão antiga. O que some é o mar vazando pelo plano do corte.
  - O vazamento aparecia como feixes azulados sobre as células do fundo duplo e sobre a chapa do piso.
- **Trecho afetado:** quadros 76–192 (86,38–90,25 s). O vazamento cresce aos poucos e é máximo em ~88,5–89,5 s, com até ~2.400 pixels alterados por quadro.
- **Fora desse trecho**, a imagem corrigida difere da entregue só no nível da variação natural entre duas renderizações iguais (87–271 pixels isolados nas bordas).

## 2. Correção

A correção é a **mesma já aplicada na avaria**: o oclusor desenhado 0,6 % mais perto da câmera, já presente em `render2.js`. **Nenhum código mudou** nesta rodada.

**Re-render:**
- Só os quadros **66–202** (86,05–90,58 s): os afetados, mais 10 quadros de margem de cada lado.
- Tudo num **único processo**, para evitar a falha não determinística vista antes em lotes paralelos.
- Os outros 185 quadros do segmento ficaram idênticos (mesmo hash).

**Não mudou:** física, câmera, animações, rótulos, enquadramentos e materiais.

## 3. Verificação

Quadros 50–220, incluindo as duas emendas:

| | Antes | Depois |
|---|---|---|
| Quadros com mais pontos isolados que antes | — | **0** |
| Piscadas locais novas (blocos de 20 × 20 px) | — | **0** |
| Cintilação média | 5,14 | 5,17 (variação entre renderizações) |
| Cintilação local, percentil 95 | 122,5 | 122,8 |

**Master recomposto a partir dos quadros**, sem render 3D:
- As mudanças estão em 85,9–90,65 s (PSNR 41,5–45 dB contra o master anterior).
- No resto, PSNR ≥ 44,5 dB. São só pequenas variações de compressão perto do trecho, em quadros-fonte que não foram tocados.

**Revisão integral:**

| Item | Resultado |
|---|---|
| Duração | 168,000 s, 5.040 quadros |
| Integridade | 0 quadros pretos, 0 trechos parados, 0 erros de decodificação |
| Narração | +3 ms, constante |
| Volume e pico | −14,1 LUFS · −2,0 dBTP |
| Saturação | nenhuma |
| Áudio | **idêntico bit a bit** ao da revisão aprovada |

**Conclusão:** a melhoria está comprovada por medição e é visível nos detalhes ampliados. Não surgiram novos artefatos.

Não houve outros ajustes de áudio ou imagem. Nada foi publicado e o render 1080 × 1920 não foi iniciado. A narração segue do plano gratuito da ElevenLabs, portanto o episódio **não está licenciado para exploração comercial** (`voz/LICENCA_NARRACAO.md`).
