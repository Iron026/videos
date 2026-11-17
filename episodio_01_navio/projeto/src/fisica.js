// Simulação determinística do calado do navio ao longo de todo o episódio.
// Pré-calculada uma única vez; cada quadro apenas amostra as tabelas (renderização em qualquer ordem).
import { tabelaHidrostatica, volumeAte, PONTAL } from './casco.js';
import { T, CARGA, ALAGAMENTO } from './roteiro.js';

const RHO = 1.025; // t/m³ (água do mar)
export const HID = tabelaHidrostatica();
export const M_BASE = HID.volume(8.0);                 // massa (em m³ de água equivalente) com 2 camadas de contêineres
export const M_CONTEINER = 30 / RHO;                   // 30 t por contêiner de 40 pés carregado
export const CALADO_MAX = 10.6;                        // linha de carga (borda-livre mínima)

// Porões alagáveis (entre anteparas) e tabela de volume interno por nível.
export const PORAO_FOLGA = 0.7;
const tabelasPorao = ALAGAMENTO.poroes.map(p => {
  const tab = []; for (let y = 0; y <= PONTAL + 1e-9; y += 0.1) tab.push(volumeAte(y, p.x0, p.x1, PORAO_FOLGA));
  return (y) => { y = Math.max(0, Math.min(PONTAL, y)); const i = Math.min(tab.length - 2, Math.floor(y / 0.1)); const f = y / 0.1 - i; return tab[i] * (1 - f) + tab[i + 1] * f; };
});

const suave = (a, b, t) => { const x = Math.min(1, Math.max(0, (t - a) / (b - a))); return x * x * (3 - 2 * x); };

// Massa de contêineres pousados até o instante t (cada um conta ao tocar o convés).
export function conteineresPousados(t, lista) {
  let n = 0; for (const c of lista) if (c.pouso !== undefined && t >= c.pouso) n++; return n;
}

export function simular(lista) {
  const dt = 1 / 600, N = Math.ceil(75.5 / dt);
  const calado = new Float32Array(N + 1), peso = new Float32Array(N + 1), empuxo = new Float32Array(N + 1);
  const niveis = ALAGAMENTO.poroes.map(() => new Float32Array(N + 1));
  let Tq = 8.0, v = 0;
  const omega = 2.4, zeta = 0.5;
  for (let i = 0; i <= N; i++) {
    const t = i * dt;
    // reinícios de cena (cortes com transição)
    if (Math.abs(t - T.entradaInicio) < dt / 2) { Tq = 0; v = 0; }
    if (Math.abs(t - T.cena8) < dt / 2) { Tq = HID.calado(M_BASE + CARGA.extra * M_CONTEINER); v = 0; }
    let M = M_BASE + conteineresPousados(t, lista) * M_CONTEINER;
    if (t >= T.cena8) M = M_BASE + CARGA.extra * M_CONTEINER;
    // alagamento: nível interno de cada porão tende ao nível externo (linha d'água)
    let Mag = 0;
    const emAlag = t >= ALAGAMENTO.inicio && t < T.cena8;
    ALAGAMENTO.poroes.forEach((p, k) => {
      const f = emAlag ? suave(p.t0, p.t1, t) : 0;
      const nivel = f * Math.min(Tq, PONTAL);
      niveis[k][i] = nivel;
      Mag += tabelasPorao[k](nivel);
    });
    const Mtot = M + Mag;
    let alvo;
    if (t < T.entradaInicio) alvo = 8.0;
    else if (t < T.entradaDescida) alvo = 0;
    else {
      alvo = HID.calado(Mtot);
      if (!isFinite(alvo) || alvo > PONTAL) alvo = PONTAL + 40; // sem equilíbrio possível: afunda
    }
    // segunda ordem amortecida em direção ao equilíbrio (inércia + amortecimento da água)
    let a = omega * omega * (alvo - Tq) - 2 * zeta * omega * v;
    if (alvo > PONTAL) a = Math.min(a, 2.2); // afundamento progressivo, sem salto
    v += a * dt; Tq += v * dt;
    calado[i] = Tq; peso[i] = Mtot; empuxo[i] = HID.volume(Math.min(Tq, PONTAL));
  }
  const amostra = (arr, t) => { const x = Math.min(N, Math.max(0, t / dt)); const i = Math.floor(x); const f = x - i; return arr[i] * (1 - f) + arr[Math.min(N, i + 1)] * f; };
  return {
    calado: t => amostra(calado, t),
    peso: t => amostra(peso, t),
    empuxo: t => amostra(empuxo, t),
    nivel: (k, t) => amostra(niveis[k], t),
  };
}
