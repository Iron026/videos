# Licença da narração do Ep. 01 — PENDÊNCIA DE USO COMERCIAL

> **O Ep. 01 NÃO está licenciado para exploração comercial.** A narração foi gerada no plano gratuito da ElevenLabs.
> Enquanto esta pendência existir, o episódio não deve ser monetizado nem apresentado como licenciado para uso
> comercial. Uma eventual publicação não comercial exige a atribuição à ElevenLabs descrita abaixo.

## Decisão registrada (19/11/2026)

- **Decisão do responsável pelo canal:** **não** contratar plano pago da ElevenLabs e **manter** a narração original já aprovada.
- **Arquivo:** `voz/narracao_ep01/Narração ep 1.mp3`, preservado sem alteração.
  - SHA-256 `79e1e8f21f30c4d00a5ec4fd4e6443b734e41ac249cdd5b170a99c7224949ba0`.
  - 170,344 s, MP3 44,1 kHz mono.
- **Voz:** Will - Deep (`CstacWqMhJQlnfLPxRG4`, clone profissional compartilhado na Voice Library da ElevenLabs).
- **Sem regeneração:** a voz não foi nem será regenerada. A ferramenta `voz/comparar_narracao.py` fica no projeto, mas **não foi e não deve ser executada** com nova narração enquanto esta decisão valer.
- **Cópia de trabalho:** `voz/narracao_ep01/trabalho/narracao_48k.wav`, normalizada, sem mudar a velocidade.
  - Dela vêm os tempos de palavras, as legendas e a sincronia dos efeitos.
  - A fala de assinatura final é removida **só na cópia de montagem**.

## Plano em que foi gerada

- A conta ElevenLabs usada estava, na verificação de 19/11/2026, no **plano gratuito** (`tier: free`).
- No ciclo atual, a conta consumiu **2.246 caracteres**, exatamente o tamanho do roteiro (`roteiro_ep01.txt`).
- O histórico não permite confirmar 100% que o arquivo saiu dessa conta, mas tudo indica que sim. Por isso o projeto o trata como **gerado no plano gratuito**.

## Restrições que se aplicam (segundo a ElevenLabs)

- **Sem licença comercial:**
  - O conteúdo do plano gratuito não pode ser usado para nenhum fim comercial.
  - Ficam excluídos, por exemplo: vídeo monetizado, publicidade, patrocínio, venda e trabalho para cliente.
  - Fonte: [ElevenLabs — Can I publish the content I generate on the platform?](https://help.elevenlabs.io/hc/en-us/articles/13313564601361)
- **Atribuição obrigatória ao publicar:**
  - Quem publica conteúdo gerado no plano gratuito deve atribuí-lo à ElevenLabs, incluindo **"elevenlabs.io"** ou **"11.ai" no título** da publicação.
  - **A atribuição não torna o uso comercial permitido.**
  - Fonte: a mesma página acima.
- **Assinar um plano depois não regulariza este arquivo:**
  - A licença comercial vale para o que é gerado **durante** uma assinatura paga ([ElevenLabs — What happens to my content after my subscription ends?](https://elevenlabs.io/docs/help-center/account/general/what-happens-to-my-content-after-my-subscription-ends)).
  - Não há regra oficial que estenda a licença a arquivos anteriores.
- **Voz da Voice Library:** não foi possível confirmar se o dono da voz Will - Deep impôs restrições adicionais. Confira na página da voz.

**Observação sobre as fontes:** os trechos acima foram obtidos por busca na web em 19/11/2026. O site da ElevenLabs não pôde ser aberto diretamente do ambiente de produção. Confira os termos vigentes na página oficial antes de qualquer publicação.

## O que isto significa para o episódio

| Item | Situação |
|---|---|
| Imagem (motor próprio, código do projeto) | sem restrição de terceiros |
| Música (síntese original do projeto) | sem restrição de terceiros |
| Efeitos sonoros (Mixkit, Sound Effects Free License) | uso comercial permitido; não redistribuir os arquivos isolados nem registrar em Content ID (`episodio/som/fontes_efeitos_hibrido.md`) |
| **Narração (ElevenLabs, plano gratuito)** | **uso não comercial; atribuição "elevenlabs.io" ou "11.ai" no título** |
| **Episódio completo** | **NÃO licenciado para exploração comercial** (a narração define o limite) |

## Como a pendência pode ser resolvida no futuro (se houver decisão)

Basta uma narração com licença comercial: regenerada num plano pago, gravada por um locutor com cessão de direitos, ou outra fonte licenciada.
- O projeto já permite trocar o áudio **sem refazer a animação**: `voz/comparar_narracao.py`, `episodio/trocar_audio.py` e `episodio/validacao_pre_render.md`, seção 4.
- Nada disso será feito sem nova autorização.
