# Ep. 02, rodada 11: dois ajustes finais (testes, nada consolidado)

**Situação:** nada foi consolidado. A transição continua "corte" por padrão e a trilha oficial continua Secret Garden até a
sua decisão. O render definitivo em 1080 segue em andamento; nenhum dos dois ajustes exige refazer o 3D.

## 1. Trilha "Spice Intrigue"

### Arquivos

| | Arquivo |
|---|---|
| Mixagem | `som/audio_ep02_r11_spice_intrigue.wav` (fora do git: contém a faixa) |
| Episódio completo | `episodio/ep02_v10_revisao_efeitos_e_spice_intrigue.mp4` |
| A/B | `episodio/previas_r10/ab_spice_intrigue.mp4`: trechos alternando A = efeitos aprovados sem música × B = efeitos + Spice Intrigue |
| Stems | voz, efeitos, mecanismo e ambiências da V10 sem mudança; música em `som/stems/ep02_musica_r10_si.wav` (fora do git) |

### Medidas no AAC final

| Métrica | Spice Intrigue | Secret Garden (referência) | Meta |
|---|---|---|---|
| Loudness | −14,1 LUFS | −14,11 | −14 |
| Pico verdadeiro | **−1,68 dBTP** | −1,60 | ≤ −1,5 |
| Voz − resto no celular simulado, p5 | 12,7 dB | 12,9 | ≥ 10 |
| Voz − resto, mediana | 26,0 dB | 25,6 | — |
| Voz − resto, pior janela | −4,0 dB (104,0 s, cauda de palavra a −44,7 dBFS) | −1,1 | — |
| Perda em mono | −0,01 dB | 0,0 | ≈ 0 |
| Último 0,5 s | −45,6 dBFS | −45,6 | silêncio |
| Narração (B − música) ÷ A nas amostras de fala | −0,001 dB | −0,002 | 0: mesmo nível |

### Correção de pico, mínima e local

- **Antes:** a primeira versão deu −1,34 dBTP no AAC, às 85,9 s (pico da narração em "ar da cozinha").
- **Correção:** −0,2 dB numa janela de ±0,2 s, com rampas de 30 ms.
- **Alcance:** 0,26 % das amostras; fora da janela, a saída é idêntica à entrada (provado).
- **Teto global:** continua −1,8, sem o −2,0 global.
- **Registro:** `testes_r10/ajuste_pico_local_spice_intrigue.json`.

### Caráter da faixa (medido; eu não escuto)

- Percussão moderada (0,16).
- Pulso em 96 BPM.
- Graves em 18 % da energia.
- A página está na categoria "comedy" do Pixabay. Se ela soa engraçada demais para "curiosidade e investigação", só a sua
  audição decide.

### Licença

Fica pendente a sua confirmação na página: o acesso automático está bloqueado. Detalhes em `licencas_r10.md`.

## 2. Transição rosto → interior azul (A4, corte às 5,737 s)

### Arquivos

| | Arquivo |
|---|---|
| Prévias de 540, janela de 4,2 a 7,2 s | `episodio/previas_r11/transicao_{corte,varredura,empurrao}.mp4` |
| Comparativo | `comparativo_transicao_lado_a_lado.mp4`: as três lado a lado, depois em câmera lenta 4× |
| Folha de quadros | `folha_transicao.jpg`: 6 instantes × 3 opções |

### Como as alternativas foram feitas

- **Sem mistura de imagens:** nenhuma das duas usa fusão/transparência entre as duas imagens. Cada pixel vem do rosto **ou**
  do interior, então a serpentina nunca aparece sobre o rosto.
- **Quadros-ponte:** foram renderizados à parte, com a mesma configuração aprovada (MSAA 4×, AO 16, bloom 0,18), em 540 e
  em 1080:
  - o rosto continuado depois do corte (A4 q33–41, mesma reação aprovada);
  - o interior antes do corte (q26–34).
- **Cenas aprovadas não mudaram:** a exportação padrão do A4 continua idêntica (174/174 quadros).

### As três opções

| Opção | O que acontece | Duração da passagem | Maior salto entre quadros |
|---|---|---|---|
| A · corte seco (atual) | troca instantânea | 1 quadro | **44,0** (um único quadro) |
| B · varredura | uma linha creme fina (mesma cor da divisória da tela) revela o interior da direita para a esquerda | 0,40 s (12 quadros) | 22,0, distribuído |
| C · empurrão | o rosto sai pela esquerda, o interior entra pela direita, com desfoque de movimento de obturador 180° | 0,30 s (9 quadros) | 24,8, distribuído |

- **Unidade do salto:** diferença média de cinza entre quadros vizinhos, de 0 a 255.
- **Referência:** o corte A3 → A4 às 4,90 s (38,2) é igual nas três opções.

### O que não muda

- **Quadros fora da janela:** idênticos ao corte, provado nos quadros compostos **antes** do codificador.
- **Resíduo de codificação:** no MP4 sobra uma diferença de 0,3 a 1,9. É do x264 (há um único quadro-chave no trecho), não
  da imagem.
- **Sem mudança em:** duração, áudio, legendas, avisos e painel térmico da direita (camadas 2D por cima, imóveis).

### Recomendação: C (empurrão)

- **Por quê:** lê-se como um movimento rápido de câmera (linguagem de cinema) e reduz o salto pela metade. Não usa elemento
  gráfico novo.
- **Contra B:** a linha que corta o rosto ao meio por 0,4 s tende ao "efeito de interface", que você evita.
- **Contra C:** por cerca de 3 quadros o rosto fica borrado, o que é próprio do movimento rápido. Se parecer forte demais,
  dá para reduzir o rastro só na montagem, sem render.
- **Em qualquer escolha:** a decisão estética é sua; eu meço, não assisto como uma pessoa.

**Nada publicado. Nenhum serviço contratado. Nenhuma voz gerada. Episódio 01 intocado.**
