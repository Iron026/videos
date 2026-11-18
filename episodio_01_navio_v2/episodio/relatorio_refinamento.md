# Ep. 01 · Refinamento final: relatório

| Entrega | Arquivo |
|---|---|
| Versão integral atualizada (169,5 s, 540 × 960, 30 fps) | `episodio/ep01_revisao_refinada.mp4` + `.validacao.json` |
| Comparativo antes/depois (lado a lado, áudio novo, 5 trechos) | `episodio/comparativo_refinamento.mp4` |
| Montagem curta só com os trechos corrigidos | `episodio/ep01_refinamento_trechos.mp4` |
| Folha antes/depois (15 instantes) | `episodio/comparativo_refinamento.jpg` |
| Versão anterior preservada | `episodio/ep01_revisao_ajustes.mp4` (quadros antigos em `quadros_revisao_antes2/`) |

**Render:**
- Só os quadros alterados, a 540 × 960 com 30 fps reais (Three.js v2, GTAO 4): **1.320 quadros em 51 min**.
- Os outros ~3.765 quadros da versão de revisão foram reaproveitados. Conferi que câmera e objetos deles são idênticos à exportação anterior.
- Não houve render integral nem 1080 × 1920.

## Correções

| # | Pedido | O que foi feito |
|---|---|---|
| 1 | **Encerramento** | <ul><li>A tela de assinatura (mascote, título e slogan) saiu. O vídeo termina no último plano da conclusão: a aérea do navio inteiro continua até **169,5 s** (antes 171,0 s).</li><li>Uma **assinatura discreta** entra integrada a esse plano, sem cena nova: mascote pequeno em círculo e "De Olho no Invisível", com fusão de 0,8 s.</li><li>Nos últimos 0,5 s o plano escurece levemente para o azul da marca.</li><li>**Áudio:** a fala de assinatura ("De Olho no Invisível. O invisível ganha forma.", 166,56–169,86 s) foi retirada **só da cópia de montagem**. O corte fica em 166,36 s, numa pausa da voz. O MP3 original continua intacto (SHA 79e1e8f2…), assim como o WAV de trabalho.</li><li>O sino e o whoosh da assinatura saíram. A trilha resolve num acorde de Ré, e trilha, mar e efeitos descem juntos em ~3 s até o silêncio, sem corte.</li><li>As legendas não mudaram (a assinatura já não tinha legenda).</li></ul> |
| 2 | **Aço do bloco** | <ul><li>**Causa:** o shader "aço escovado" tinha relevo de altíssima frequência (720 ciclos/m) e metal 100%. No bloco de 1,6 m isso virava ruído de pixels com reflexos azulados cintilando.</li><li>**Correção:** nova variante **aço maciço** no shader: sem escovação; manchas de laminação largas e suaves (±7%); rugosidade 0,30 com pouca variação (±20%); grão fino que se apaga sozinho quando fica menor que o pixel (sem cintilação); metal 0,9; bordas definidas pelo chanfro.</li><li>O mesmo material vale para **todos** os blocos: abertura, retomada (1:15), experimento e conclusão.</li><li>Geometria, massa e física não mudaram.</li></ul> |
| 3 | **Soldagem** (0:23) | <ul><li>**Arco branco-azulado:** núcleo intenso e halo, tremulando de forma irregular a 30 Hz. Abre em dois cordões, com uma pausa curta entre eles.</li><li>**Luz do arco nas chapas vizinhas:** brilho aditivo com queda radial (~3,4 m) que pulsa junto com o arco.</li><li>**Faíscas alaranjadas balísticas:** saem com velocidades variadas, caem com a gravidade (9,81 m/s²) e vivem 0,16–0,55 s. Cada uma renasce várias vezes. Têm rastro proporcional à velocidade, com cabeça quente e cauda que se apaga.</li><li>**Som:** zumbido elétrico do arco, crepitar e chiado das faíscas.</li><li>**No motor:** só um material leve de brilho (`brilho`), aditivo e com tremulação no shader. Não há luzes dinâmicas novas.</li></ul> |
| 4 | **Empuxo** (0:56–1:03): sumiço abrupto | <ul><li>**Causa:** as setas eram emissivas opacas e só podiam encolher ou sumir. O mapa de pressão sumia em 0,3 s, e havia um corte de câmera em 59,6 s no meio da explicação.</li><li>**Correção:** setas e mapa agora desbotam por opacidade, e a evolução é contínua:<ol><li>pressões no contorno;</li><li>os dois lados **se empurram** (57,3 s) e depois **deslizam um para o outro e desbotam** (58,35–59,2 s), com o rótulo "Laterais se anulam";</li><li>no bojo, a seta oblíqua dá lugar à sua **componente vertical** (fusão cruzada de 0,9 s);</li><li>todas as verticais (fundo e bojo) convergem para B e **se fundem** enquanto o empuxo cresce (61,25–62,0 s);</li><li>o mapa de pressão se apaga em 1,3 s.</li></ol></li><li>Os planos 28 e 29 viraram **um só movimento de câmera**, sem corte.</li><li>A ciência não mudou: os pares horizontais se anulam e o empuxo é a soma das componentes verticais em toda a superfície molhada.</li></ul> |
| 5 | **Retomada do bloco** (1:15) | <ul><li>O plano começa no **mesmo cais da abertura**, com o mesmo enquadramento e a mesma câmera da abertura, em tempo de cena. O chip "Retomando o experimento" e o rótulo "O mesmo bloco do início" identificam a retomada.</li><li>O bloco é empurrado, sai da borda e cai na mesma trajetória integrada da abertura, em tempo real. Impacto em 76,13 s, com respingo e ondas.</li><li>Logo depois, a velocidade da cena **desce suavemente** até a câmera lenta (chip "Câmera lenta"), sem salto de posição nem de ritmo.</li><li>A câmera passa pela linha d'água e chega ao close das forças **sem corte**, numa transição de 0,7 s. As setas de peso e empuxo crescem depois que o bloco está na água.</li><li>Dali em diante, o trecho segue igual ao aprovado.</li><li>**Som:** arrasto do aço no concreto, queda, impacto, bolhas.</li></ul> |

## Validação

| Item | Resultado |
|---|---|
| Formato | 540 × 960, 30,0 fps, **5.085 quadros, 169,5 s** |
| Quadros pretos / congelamentos ≥ 1,5 s | nenhum / nenhum |
| Loudness | −14,0 LUFS, pico −2,0 dBTP |
| Sincronia da narração | +3 ms em 10, 85 e 160 s (correlação com o MP3 original) |
| Final do áudio | voz até 166,36 s → trilha e mar de −38 dB a silêncio entre 166,4 e 169,5 s, sem degrau |
| Continuidade | abertura → retomada com o mesmo cais, o mesmo bloco e a mesma câmera; empuxo sem corte entre 56,6 e 63,1 s; conclusão termina no navio |

**Testes de quadro (270 × 480) antes do render, ajustados:**
- **Faíscas:** saíam brancas e saturadas. Passaram a usar material de brilho, alaranjado, com cauda.
- **Assinatura:** o sublinhado encostava no texto e foi baixado.

## O que ainda pode ser notado

1. **Faíscas a 540 × 960:** são finas (3 cm de raio), e a leitura completa fica melhor na versão de 1080. As que caem para dentro do casco desaparecem atrás da chapa (oclusão correta).
2. **Luz da solda:** é um brilho aditivo, não uma luz real. Não projeta sombras dos andaimes nem acende o primer de forma direcional.
3. **Último plano:** a assinatura discreta aparece por ~3 s.
4. **Pendências antigas, não tratadas nesta rodada:**
   - água em diorama nos planos submersos;
   - espuma da proa discreta;
   - trim de 0,71° sutil.

**Próximo passo:** aguardando sua aprovação. O render definitivo a 1080 × 1920 (≈ 9–14 h) não foi iniciado. Nada foi publicado e nenhum serviço foi contratado.
