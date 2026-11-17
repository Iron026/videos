// Trilha de câmera por quadros-chave. Interpolação cúbica de Hermite (tangentes Catmull-Rom)
// => velocidade contínua. Um quadro-chave com corte:true inicia um novo trecho sem interpolar
// com o anterior (usado apenas sob as transições de cor da marca).
// Cada chave: [t, [px,py,pz], [alvoX,alvoY,alvoZ], fov(graus vertical), opções]
export const CHAVES = [
  // Cena 01 — aproximação rápida, queda do bloco, fatia do oceano
  [0.0, [330, 22, 420], [10, 9, 0], 42],
  [2.6, [190, 15, 190], [40, 6, 0], 44],
  [4.1, [176, 9, 120], [100, 0, 0], 46],
  [5.6, [178, 0, 128], [116, -12, -4], 48],
  [7.9, [168, -12, 112], [118, -24, -4], 50],
  // Cena 02 — atravessando o casco
  [8.8, [110, 6, 120], [40, 2, 0], 48],
  [10.0, [40, 8, 70], [0, 2, -8], 52],
  [11.3, [40, 22, 120], [-5, 2, -6], 50],
  [12.8, [75, 28, 175], [-12, 0, -6], 46],
  // Cena 03a — bloco maciço no fundo
  [14.6, [168, -24, 36], [136, -31, -3.5], 44],
  [17.0, [158, -27, 30], [137, -31.5, -3.5], 42],
  [19.75, [150, -12, 52], [128, -24, -3.5], 44],
  // Cena 03b — seção transversal a meia-nau (após transição)
  [19.75, [95, 34, 92], [6, 0, 0], 46, { corte: true }],
  [23.5, [92, 12, 56], [6, -1, 0], 46],
  [27.75, [88, 2, 22], [6, -1, 0], 48],
  // Cena 04 — entrada no mar e volume deslocado
  [27.75, [175, 4, 175], [0, -2, 0], 46, { corte: true }],
  [31.6, [150, -4, 150], [5, -4, 0], 46],
  [35.8, [128, -9, 138], [5, -5, 0], 46],
  // Cena 05 — forças
  [40.5, [118, -6, 152], [3, -6, 0], 48],
  [46.8, [104, -4, 168], [3, -5, 0], 48],
  // Cena 06 — contêineres
  [50.5, [96, 10, 178], [0, 2, 0], 48],
  [55.75, [64, 2, 128], [0, -1, 0], 46],
  // Cena 07 — alagamento (corte longitudinal)
  [55.75, [150, 26, 160], [-8, -2, -4], 46, { corte: true }],
  [59.5, [135, 18, 150], [-8, -4, -4], 46],
  [62.75, [128, 12, 145], [-8, -9, -4], 46],
  // Cena 08 — conclusão
  [62.75, [150, -6, 112], [8, -3, 0], 46, { corte: true }],
  [66.5, [175, 6, 175], [4, -2, 0], 45],
  [70.3, [235, 34, 250], [0, 0, 0], 42],
  [75.0, [255, 44, 275], [0, 2, 0], 42],
];

function trechos() {
  const out = []; let atual = [];
  for (const k of CHAVES) {
    if (k[4] && k[4].corte && atual.length) { out.push(atual); atual = []; }
    atual.push(k);
  }
  out.push(atual); return out;
}
const TRECHOS = trechos();

function hermite(ks, t, get) {
  if (t <= ks[0][0]) return get(ks[0]);
  if (t >= ks[ks.length - 1][0]) return get(ks[ks.length - 1]);
  let i = 0; while (t > ks[i + 1][0]) i++;
  const k0 = ks[i], k1 = ks[i + 1];
  const t0 = k0[0], t1 = k1[0], h = t1 - t0, s = (t - t0) / h;
  const v0 = get(k0), v1 = get(k1);
  const tang = (j) => {
    if (j <= 0 || j >= ks.length - 1) return v0.map(() => 0);
    const a = get(ks[j - 1]), b = get(ks[j + 1]);
    return a.map((_, c) => (b[c] - a[c]) / (ks[j + 1][0] - ks[j - 1][0]));
  };
  const m0 = tang(i), m1 = tang(i + 1);
  const h00 = 2 * s ** 3 - 3 * s ** 2 + 1, h10 = s ** 3 - 2 * s ** 2 + s, h01 = -2 * s ** 3 + 3 * s ** 2, h11 = s ** 3 - s ** 2;
  return v0.map((_, c) => h00 * v0[c] + h10 * h * m0[c] + h01 * v1[c] + h11 * h * m1[c]);
}

export function estadoCamera(t) {
  let tr = TRECHOS[0];
  for (const x of TRECHOS) if (t >= x[0][0]) tr = x;
  const get = (k) => [...k[1], ...k[2], k[3]];
  const v = hermite(tr, t, get);
  return { pos: v.slice(0, 3), alvo: v.slice(3, 6), fov: v[6] };
}
