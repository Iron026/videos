# Ep. 01 · Validação final antes do render

**O que esta rodada não fez:**
- **Não alterou** imagem nem som: a montagem aprovada (`ep01_revisao_polimento.mp4`, 168,0 s) e a mixagem híbrida continuam **idênticas byte a byte**.
- Não iniciou o render de 1080 × 1920.
- Não publicou nada.
- Não gerou nenhuma voz.
- Não gastou crédito nenhum.

## 1. Montagem e segmentos aprovados

- `ep01_revisao_polimento.mp4` não foi tocado; segue igual ao commit `2823444`.
- Nenhum segmento visual foi mudado nem re-renderizado.
- Mudanças em `montar_ep01.py`, todas **desligadas por padrão** (sem elas a montagem sai igual):

  | Variável | O que faz |
  |---|---|
  | `SEM_LEGENDAS=1` | gera o master de imagem sem legendas |
  | `CRF_EP01` | qualidade do vídeo |
  | `NARRACAO_EP01_DIR` | legendas de outra narração |

## 2. Som híbrido e stems

- **Mixagem e 4 stems sem mudança:** `audio_ep01_hibrido.wav` e os stems de narração, efeitos, ambiências e música têm o mesmo SHA-256 de antes desta rodada (verificado depois de cada alteração no código).
- **Novo: stems por grupo de substituição** em `episodio/stems/grupos/`:
  - um stem de efeitos e um de ambiências por grupo;
  - a mesma cadeia de mixagem do episódio: reverberação, nível, ducking, fade e master;
  - grupo + `resto` reconstroem exatamente os stems (erro máximo −132 dBFS).
  - Assim dá para ouvir um grupo isolado, ou o episódio sem ele.

| Grupo | Ativo (s) | Sons |
|---|---|---|
| **Estaleiro** (ambiente, encaixe, solda, chapas, corte do casco) | 15,2–42,5 | 26 |
| **Guindastes** (pórtico do estaleiro e portêineres: motores, carros, cabos) | 15,1–117,8 | 12 |
| **Porto** (ambiente, empilhadeiras, pousos de contêiner, água no casco, marcas) | 94,6–134,7 | 17 |
| **Dique** (comporta, jatos, enchimento) | 41,3–48,8 | 10 |
| **Inundação da avaria** (ruptura, jato, porão enchendo, rangidos, divisórias) | 134,0–155,1 | 24 |

- **Mapa de troca:** `som/mapa_substituicao.md` lista cada som com:
  - instante e duração;
  - ID e nome da gravação;
  - se é **reserva** — os 11 casos em que o Commons não pôde ser baixado;
  - o uso.
- **Troca depois da sua escuta, sem editar código e sem refazer animação:**
  1. Coloque o arquivo em `som/bib/manual/`.
  2. Registre-o em `som/substituicoes.json`, com o ID original, título, autor, URL e licença.
  3. Rode `som_hibrido.py` e `registro_hibrido.py`.

  Ele entra nos mesmos instantes, camadas e níveis, e o registro de licenças é atualizado.
- **Os 11 arquivos do Commons:** não insisti no download, como você permitiu. Os substitutos atuais ficam até a sua escuta.

## 3. Licença da narração — **é preciso regenerar antes da publicação comercial**

**O que verifiquei:**
- A conta ElevenLabs conectada a esta sessão está no **plano gratuito** (`tier: free`).
- Ela consumiu **2.246 caracteres** no ciclo atual: exatamente o tamanho do roteiro do Ep. 01. Tudo indica que `Narração ep 1.mp3` foi gerada nesse plano.
- O registro do projeto (`voz/voz.json`) já anotava que o plano gratuito é "só para avaliação, não comercial".
- **Não consigo confirmar** pelo histórico em qual plano o arquivo foi gerado. Se ele veio de outra conta, paga, o quadro muda: me diga.

**O que dizem as regras da ElevenLabs:**
- Não consegui abrir o site da ElevenLabs desta sessão (o domínio não está liberado na rede). O que segue vem de busca na web: as páginas oficiais da central de ajuda, mais guias de terceiros onde indicado.
- **Plano gratuito:** sem licença comercial, não pode ser usado para nenhum fim comercial. Quem publica deve atribuir à ElevenLabs ("elevenlabs.io" ou "11.ai" no título). **A atribuição não torna o uso comercial permitido.** [Ajuda ElevenLabs — Can I publish the content I generate on the platform?](https://help.elevenlabs.io/hc/en-us/articles/13313564601361)
- **Plano pago:** o que for gerado **durante** a assinatura pode ser usado comercialmente, por tempo indeterminado, mesmo depois de cancelar. O que foi gerado fora de uma assinatura sempre exige atribuição. [Ajuda ElevenLabs — What happens to my content after my subscription ends?](https://elevenlabs.io/docs/help-center/account/general/what-happens-to-my-content-after-my-subscription-ends)
- **Assinar depois não regulariza o arquivo antigo:** não achei declaração oficial de que isso aconteça. Guias de terceiros recomendam **regenerar durante a assinatura paga** ([licenseorg](https://licenseorg.com/blog/elevenlabs-licensing-guide-ai-voices), [terms.law](https://terms.law/ai-output-rights/elevenlabs/)).
- **Plano mais barato com licença comercial:** Starter, cerca de US$ 6/mês ou US$ 5/mês no anual, com ~30.000 créditos, segundo guias de terceiros ([dupple](https://dupple.com/learn/is-elevenlabs-free)). **Confirme o preço na página oficial.**
  - O roteiro tem 2.246 caracteres, então cabem várias tomadas.
- **Voz "Will - Deep" (clone profissional compartilhado na Voice Library):** não encontrei a regra de uso comercial de vozes da biblioteca. Na própria ElevenLabs, ao gerar, confira se a página da voz não traz restrição do dono, como uso comercial ou aviso de retirada.

**Conclusão:** para monetizar, a narração precisa ser **regenerada durante um plano pago**, com a mesma voz, modelo e ajustes, guardando o comprovante. Isso é decisão sua e precisa ser feito **por você, no site, do seu computador**:
- não contrato planos;
- o conector desta sessão teve o acesso gratuito bloqueado por "uso de proxy";
- a regra do projeto proíbe gerar pela infraestrutura daqui.

**Regenerar exige:**
1. Plano pago ativo.
2. Mesma voz, mesmo modelo e mesmos ajustes do arquivo atual: Will - Deep, stability 0,50, similarity 0,75, style 0, speed 1,0. O modelo deve ser **confirmado no seu histórico** (o nome da amostra sugere v4).
3. Texto de `voz/narracao_ep01/roteiro_ep01.txt`.
4. Salvar o MP3 original sem editar.

## 4. Impacto de uma narração nova na sincronização

Uma voz regenerada não sai com os mesmos tempos. Criei `voz/comparar_narracao.py` para medir isso **antes** de qualquer render.

**O que a ferramenta faz:**
1. Alinha acusticamente a narração atual com a nova, sem depender de reconhecimento de fala.
2. Leva cada frase e cada palavra para o tempo novo.
3. Relata:
   - a deriva se a voz nova entrasse como está;
   - a deriva depois do encaixe;
   - quais blocos precisariam acelerar.
4. Gera uma **versão encaixada**: cada **bloco de fala** (frases sem pausa entre si) começa no mesmo instante do bloco atual. Só acelera um bloco se ele não couber até o próximo, sem mudar a altura (rubberband). Acima de 6% de aceleração, o bloco é apontado para revisão.

**Teste da ferramenta:** sem uma narração nova real, simulei três "narrações novas" a partir da atual:
- ritmo de cada bloco de −8% a +10%;
- pausas ×0,7 a ×1,5;
- outro timbre e outro volume.

Como os tempos verdadeiros são conhecidos, a precisão é mensurável:

| Medida (3 simulações) | Resultado |
|---|---|
| Tempo de palavra | erro mediano 3 ms · p95 7 ms |
| Início de frase | erro mediano 4 ms · máx. 17 ms (< ½ quadro) |
| Ataque de cada bloco no arquivo encaixado × narração atual | mediana 0 ms · máx. 10 ms |
| Deriva sem encaixe (para comparação) | até 2,7 s, e 46–48 das 49 frases fora por mais de 1 quadro |
| Aceleração necessária | 7–9 blocos de 42, no máximo 4,5% (nenhum acima do limite de 6%) |
| Frases ligadas por vírgula (dentro de um bloco) | podem deslocar até 0,2–0,3 s, porque o ritmo interno da voz nova manda |

**Limite:** é uma simulação. Com o arquivo real, a ferramenta dá os números verdadeiros, e eu os reporto **antes** de qualquer render.

**Fluxo quando você tiver o MP3 licenciado:**
```
python3 voz/comparar_narracao.py "<novo>.mp3" voz/narracao_nova_encaixada
#   → comparacao_tempos.json: deriva por frase, blocos acelerados, blocos acima de 6% (relatório para você decidir)
NARRACAO_EP01_DIR=voz/narracao_nova_encaixada SUFIXO_HIBRIDO=_vozpaga python3 episodio/som/som_hibrido.py
NARRACAO_EP01_DIR=voz/narracao_nova_encaixada python3 episodio/trocar_audio.py episodio/audio_ep01_hibrido_vozpaga.wav episodio/ep01_revisao_vozpaga.mp4
```

Testei esse fluxo de ponta a ponta com a narração simulada:
- **mixagem:** −14,07 LUFS e −1,8 dBTP; 92% da fala ≥ 10 dB acima do fundo no teste de celular;
- **montagem:** as legendas seguem a voz nova.

## 5. Preservação e troca de áudio sem refazer a animação

**No git (preservado):**
- todo o código: construtores de cena, motor, montagem, som, registros e ferramentas de voz;
- a revisão aprovada (`ep01_revisao_polimento.mp4`);
- **novo: `ep01_master_imagem_sem_legendas.mp4`** — imagem final da revisão, com rótulos e avisos, **sem legendas**; 64 MB, 168,0 s, 5.040 quadros.

**Só neste contêiner (temporário):**
- os quadros de revisão (431 MB);
- as cenas exportadas (2,0 GB);
- os WAVs (os do Mixkit não podem ir para o git).

**Reprodutibilidade conferida:**
- **Cena reexportada (s13):** idêntica byte a byte à aprovada.
- **Quadro re-renderizado:** igual ao aprovado (PSNR 50,5 dB; a diferença é só de compressão JPEG).
- Portanto os quadros podem ser refeitos do código a qualquer momento.

**Trocar o áudio sem quadros nem render 3D:** `episodio/trocar_audio.py` usa o master, queima as legendas da narração escolhida e coloca a nova mixagem com o mesmo controle de loudness e pico.

| Teste com a mixagem atual | Resultado |
|---|---|
| Tempo de processamento | 75 s |
| Áudio | −14,0 LUFS · −2,4 dBTP |
| Imagem × revisão aprovada | PSNR médio 43,7 dB (equivalente visualmente) |

**Render definitivo:** os quadros de 1080 × 1920 serão renderizados de novo (perfil `final`). A imagem não depende do áudio. O áudio escolhido entra pelas mesmas variáveis (`AUDIO_EP01`, `NARRACAO_EP01_DIR`).

## 6. O que decide o render definitivo

1. **Sua escuta** do som híbrido: use os stems de grupo e o mapa de troca.
2. **Narração licenciada:** regenerar num plano pago. Rodo `comparar_narracao.py` e reporto o impacto real na sincronização antes de qualquer render.
3. **Nenhum bloqueio técnico conhecido.**
