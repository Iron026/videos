# Ep. 02 · Plano de sound design (v1, antes da narração)

**Estado:** o animatic sai **sem som**. O som é montado depois da narração aprovada, porque ducking, inteligibilidade e
posição dos efeitos dependem dos instantes reais das palavras (lição do Ep. 01). A arquitetura é a do Ep. 01
(`som_refinado.py`, `movimento.py`): stems separados, ganhos fixos, gerador aleatório isolado e loudness medido no AAC.

## Fontes (regras do Ep. 01)
- Gravações reais com licença verificada: Mixkit (uso comercial, sem redistribuir o arquivo isolado) e Wikimedia Commons CC0.
  CC BY só com créditos. **Nunca** CC BY-NC nem material tirado do YouTube.
- Registro automático de procedência (arquivo, URL, licença e uso), com as substituições documentadas.
- **Não** usar sons de água para o refrigerante; **não** usar motor industrial ou automotivo para o compressor.

## Camadas por cena
| Cena | Camadas | Ligado a |
|---|---|---|
| Cozinha | Ambiente doméstico discreto (geladeira ligada ao fundo, ar parado, um relógio distante opcional) | Distância da câmera à geladeira |
| Porta | Estalo da vedação ao abrir e ao fechar; lâmpada interna sem som | Curva de ângulo da porta (abertura e fechamento) |
| Interior | Ambiente "contido": o zumbido fica abafado e mais grave | Plano (dentro × fora) |
| Compressor | Zumbido de 60 Hz com harmônicos, nível baixo; no corte (E3), pulsação mecânica sincronizada às válvulas | `compressor_mec.ciclo()`: abertura de sucção e descarga |
| Capilar | Chiado fino e baixo no fim do capilar (expansão); nada antes da metade | Posição da câmera no capilar (s > 0,53) |
| Porta aberta (I) | Compressor contínuo, sem desligar | Curva `uTrabVel` |
| Fim (J4) | O compressor desliga suavemente (termostato) junto da última palavra | Fim da fala |

## O que NÃO terá som
Feixes de calor, pulso do circuito, rótulos, manômetros, varredura térmica e cortes comuns. Sem graves cinematográficos.

## Metas técnicas (iniciais, a verificar)
−14 LUFS e pico verdadeiro ≤ −1,5 dBTP **no AAC**; voz ≥ 10 dB acima do resto no celular simulado; mono sem perda.
