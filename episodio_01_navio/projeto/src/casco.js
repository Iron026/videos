// Geometria procedural do casco do navio porta-contêineres.
// Uma única função de forma (meiaBoca) alimenta: malha 3D, cálculo de volume/calado,
// máscara da água nos cortes técnicos (GLSL) e o volume deslocado destacado.
// Coordenadas locais do navio (metros): x = popa(-) → proa(+), y = quilha(0) → convés(PONTAL), z = través.
import * as THREE from 'three';

export const POPA = -100, PROA = 104, MEIA_BOCA = 16, PONTAL = 18, RAIO_BOJO = 2.6;

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };

// Altura da quilha (fundo) ao longo do comprimento: sobe na popa (painel de popa acima do fundo).
export function quilha(x) {
  const v = clamp((-58 - x) / 42, 0, 1);
  const b = clamp((x - 88) / 16, 0, 1);
  return 8.0 * Math.pow(v, 1.7) + 3.0 * b * b;
}
// Limite da proa em função da altura (roda de proa inclinada).
export function limiteProa(y) { return 97 + 7 * Math.pow(clamp(y / PONTAL, 0, 1), 1.4); }

// Meia-boca (distância do plano diametral ao costado) na posição x e altura y.
export function meiaBoca(x, y) {
  const k = quilha(x);
  if (y < k - 1e-6 || y > PONTAL + 1e-6 || x < POPA || x > PROA) return 0;
  const xe = limiteProa(y);
  if (x >= xe) return 0;
  // contorno do convés e do fundo
  const u = clamp((x - 38) / (xe - 38), 0, 1);             // afinamento da proa
  const v = clamp((-62 - x) / 38, 0, 1);                    // afinamento da popa
  const bConves = MEIA_BOCA * Math.pow(1 - Math.pow(u, 2.1), 0.62) * (1 - 0.2 * v * v);
  const ub = clamp((x - 28) / (xe - 28), 0, 1);
  const bFundo = MEIA_BOCA * Math.pow(1 - Math.pow(ub, 1.5), 0.85) * (1 - Math.pow(clamp((-48 - x) / 52, 0, 1), 1.25));
  const s = clamp((y - k) / Math.max(PONTAL - k, 1e-3), 0, 1);
  let b = bFundo + (bConves - bFundo) * (1 - Math.pow(1 - s, 2.2));
  // arredondamento do bojo
  const r = Math.min(RAIO_BOJO, b * 0.5);
  const h = y - k;
  if (h < r) b -= r - Math.sqrt(Math.max(0, r * r - (r - h) * (r - h)));
  return Math.max(0, b);
}

// Mesma função em GLSL (deve permanecer idêntica à versão JS).
export const GLSL_CASCO = /* glsl */`
const float POPA=${POPA.toFixed(1)}, PROA=${PROA.toFixed(1)}, MEIA_BOCA=${MEIA_BOCA.toFixed(1)}, PONTAL=${PONTAL.toFixed(1)}, RAIO_BOJO=${RAIO_BOJO.toFixed(2)};
float quilhaG(float x){ float v=clamp((-58.0-x)/42.0,0.0,1.0); float b=clamp((x-88.0)/16.0,0.0,1.0); return 8.0*pow(v,1.7)+3.0*b*b; }
float limiteProaG(float y){ return 97.0+7.0*pow(clamp(y/PONTAL,0.0,1.0),1.4); }
float meiaBocaG(float x,float y){
  float k=quilhaG(x);
  if(y<k-1e-4||y>PONTAL+1e-4||x<POPA||x>PROA) return 0.0;
  float xe=limiteProaG(y); if(x>=xe) return 0.0;
  float u=clamp((x-38.0)/(xe-38.0),0.0,1.0); float v=clamp((-62.0-x)/38.0,0.0,1.0);
  float bC=MEIA_BOCA*pow(1.0-pow(u,2.1),0.62)*(1.0-0.2*v*v);
  float ub=clamp((x-28.0)/(xe-28.0),0.0,1.0);
  float bF=MEIA_BOCA*pow(max(1.0-pow(ub,1.5),0.0),0.85)*(1.0-pow(clamp((-48.0-x)/52.0,0.0,1.0),1.25));
  float s=clamp((y-k)/max(PONTAL-k,1e-3),0.0,1.0);
  float b=bF+(bC-bF)*(1.0-pow(1.0-s,2.2));
  float r=min(RAIO_BOJO,b*0.5); float h=y-k;
  if(h<r) b-=r-sqrt(max(0.0,r*r-(r-h)*(r-h)));
  return max(0.0,b);
}
// p em coordenadas locais do navio; folga>0 encolhe o sólido (para testar "dentro do porão").
bool dentroCasco(vec3 p,float folga){
  if(p.y>PONTAL-folga) return false;
  float b=meiaBocaG(p.x,p.y);
  return b>folga && abs(p.z)<b-folga && p.y>quilhaG(p.x)+folga;
}
`;

// ---------- Hidrostática ----------
// Volume do casco abaixo do plano y = calado (coordenadas locais), por integração numérica.
export function volumeAte(calado, x0 = POPA, x1 = PROA, folga = 0) {
  const nx = 220, ny = 60; let V = 0;
  const dx = (x1 - x0) / nx;
  for (let i = 0; i < nx; i++) {
    const x = x0 + (i + 0.5) * dx; const k = quilha(x) + folga;
    const top = Math.min(calado, PONTAL - folga); if (top <= k) continue;
    const dy = (top - k) / ny; let A = 0;
    for (let j = 0; j < ny; j++) { const y = k + (j + 0.5) * dy; A += 2 * Math.max(0, meiaBoca(x, y) - folga) * dy; }
    V += A * dx;
  }
  return V;
}
// Centroide (x, y) do volume submerso — centro de carena (B).
export function centroCarena(calado) {
  const nx = 120, ny = 40; let V = 0, Mx = 0, My = 0; const dx = (PROA - POPA) / nx;
  for (let i = 0; i < nx; i++) {
    const x = POPA + (i + 0.5) * dx; const k = quilha(x); const top = Math.min(calado, PONTAL); if (top <= k) continue;
    const dy = (top - k) / ny;
    for (let j = 0; j < ny; j++) { const y = k + (j + 0.5) * dy; const a = 2 * meiaBoca(x, y) * dy * dx; V += a; Mx += a * x; My += a * y; }
  }
  return { x: Mx / V, y: My / V, V };
}
// Tabela calado → volume, para inversão rápida.
export function tabelaHidrostatica() {
  const passos = [];
  for (let T = 0; T <= PONTAL + 1e-9; T += 0.1) passos.push([T, volumeAte(T)]);
  return {
    volume(T) { T = clamp(T, 0, PONTAL); const i = Math.min(passos.length - 2, Math.floor(T / 0.1)); const f = (T - passos[i][0]) / 0.1; return passos[i][1] * (1 - f) + passos[i + 1][1] * f; },
    calado(V) { if (V <= 0) return 0; for (let i = 0; i < passos.length - 1; i++) if (passos[i + 1][1] >= V) { const f = (V - passos[i][1]) / (passos[i + 1][1] - passos[i][1]); return passos[i][0] + f * 0.1; } return Infinity; },
    max: passos[passos.length - 1][1],
  };
}

// ---------- Malhas ----------
// Estações ao longo do comprimento, mais densas nas extremidades.
function estacoes(x0, x1, n) {
  const xs = [];
  for (let i = 0; i <= n; i++) { const t = i / n; xs.push(x0 + (x1 - x0) * t); }
  // refinamento extra perto da proa/popa
  const extra = [];
  for (const x of [POPA + 0.5, POPA + 2, 96, 98, 99.5, 100.5, 101.5, 102.5, 103.3, 103.8]) if (x > x0 && x < x1) extra.push(x);
  return [...new Set([...xs, ...extra])].sort((a, b) => a - b);
}
// Alturas amostradas no perfil (densas perto do fundo, para o bojo).
function alturas(k, topo, n) {
  const ys = [];
  for (let j = 0; j <= n; j++) { const t = j / n; ys.push(k + (topo - k) * (t < 0.3 ? Math.pow(t / 0.3, 1.6) * 0.3 : t)); }
  return ys;
}

/**
 * Sólido fechado do casco: superfície do costado+fundo, tampa superior (plano y=topo) e tampas nas
 * extremidades x0/x1 quando cortadas. folga>0 gera o casco interno (normais para dentro se inverter=true).
 */
export function solidoCasco({ x0 = POPA, x1 = PROA, topo = PONTAL, folga = 0, inverter = false, nx = 170, ny = 26, tampaTopo = true } = {}) {
  const pos = [], idx = [];
  const xs = estacoes(x0, x1, nx);
  const secoes = [];
  for (const x of xs) {
    const k = quilha(x) + folga; const t = Math.min(topo, PONTAL - (folga > 0 ? 0 : 0));
    const pts = [];
    if (t > k + 1e-3) {
      const ys = alturas(k, t, ny);
      // lado bombordo (z<0) de cima para baixo, fundo, boreste (z>0) de baixo para cima
      const lado = ys.map(y => [y, Math.max(0, meiaBoca(x, Math.min(y, PONTAL)) - folga)]);
      for (let j = lado.length - 1; j >= 0; j--) pts.push([x, lado[j][0], -lado[j][1]]);
      pts.push([x, k, 0]);
      for (let j = 0; j < lado.length; j++) pts.push([x, lado[j][0], lado[j][1]]);
    } else {
      for (let j = 0; j < 2 * (ny + 1) + 1; j++) pts.push([x, Math.max(k, t), 0]);
    }
    secoes.push(pts);
  }
  const m = secoes[0].length;
  for (const s of secoes) for (const p of s) pos.push(...p);
  for (let i = 0; i < secoes.length - 1; i++) for (let j = 0; j < m - 1; j++) {
    const a = i * m + j, b = (i + 1) * m + j, c = (i + 1) * m + j + 1, d = i * m + j + 1;
    idx.push(a, d, b, b, d, c);
  }
  // tampa superior (plano do convés ou da linha d'água): faixa entre pontos extremos das seções
  if (tampaTopo) for (let i = 0; i < secoes.length - 1; i++) {
    const a = i * m, b = i * m + m - 1, c = (i + 1) * m, d = (i + 1) * m + m - 1;
    idx.push(a, c, b, b, c, d);
  }
  // tampas das extremidades (leque a partir do centro da seção)
  const tampa = (i, sentido) => {
    const s = secoes[i]; let cy = 0; for (const p of s) cy += p[1]; cy /= s.length;
    const base = pos.length / 3; pos.push(s[0][0], cy, 0);
    for (let j = 0; j < m - 1; j++) sentido > 0 ? idx.push(base, i * m + j, i * m + j + 1) : idx.push(base, i * m + j + 1, i * m + j);
    // fecha o topo
    sentido > 0 ? idx.push(base, i * m + m - 1, i * m) : idx.push(base, i * m, i * m + m - 1);
  };
  tampa(0, 1); tampa(secoes.length - 1, -1);
  if (inverter) for (let i = 0; i < idx.length; i += 3) { const t = idx[i + 1]; idx[i + 1] = idx[i + 2]; idx[i + 2] = t; }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

/** Contorno horizontal do casco na altura y (linha d'água / convés), como lista de pontos 3D fechada. */
export function contornoNaAltura(y, folga = 0, n = 200) {
  const pts = [];
  const xs = []; for (let i = 0; i <= n; i++) xs.push(POPA + (PROA - POPA) * i / n);
  const vivos = xs.filter(x => meiaBoca(x, y) - folga > 0.01 && quilha(x) < y);
  for (const x of vivos) pts.push(new THREE.Vector3(x, y, meiaBoca(x, y) - folga));
  for (let i = vivos.length - 1; i >= 0; i--) pts.push(new THREE.Vector3(vivos[i], y, -(meiaBoca(vivos[i], y) - folga)));
  if (pts.length) pts.push(pts[0].clone());
  return pts;
}

/** Placa horizontal (convés, teto do duplo fundo) com espessura, recortada pelo contorno do casco. */
export function placaHorizontal(y, espessura, folga, x0 = POPA, x1 = PROA, n = 160) {
  const shape = new THREE.Shape();
  const xs = []; for (let i = 0; i <= n; i++) xs.push(x0 + (x1 - x0) * i / n);
  const vivos = xs.filter(x => meiaBoca(x, y) - folga > 0.05 && quilha(x) < y - 0.05);
  if (vivos.length < 2) return null;
  vivos.forEach((x, i) => { const b = meiaBoca(x, y) - folga; i ? shape.lineTo(x, b) : shape.moveTo(x, b); });
  for (let i = vivos.length - 1; i >= 0; i--) shape.lineTo(vivos[i], -(meiaBoca(vivos[i], y) - folga));
  const g = new THREE.ExtrudeGeometry(shape, { depth: espessura, bevelEnabled: false, curveSegments: 1 });
  g.rotateX(Math.PI / 2); // shape (x, z) -> plano horizontal; extrusão para baixo
  g.translate(0, y, 0);
  return g;
}

/** Antepara transversal (seção do casco na posição x) com espessura. */
export function antepara(x, espessura, folga, topo = PONTAL) {
  const k = quilha(x) + folga; const ys = alturas(k, topo, 30);
  const shape = new THREE.Shape();
  const lado = ys.map(y => [y, Math.max(0, meiaBoca(x, Math.min(y, PONTAL)) - folga)]);
  shape.moveTo(-lado[lado.length - 1][1], lado[lado.length - 1][0]);
  for (let j = lado.length - 1; j >= 0; j--) shape.lineTo(-lado[j][1], lado[j][0]);
  for (let j = 0; j < lado.length; j++) shape.lineTo(lado[j][1], lado[j][0]);
  const g = new THREE.ExtrudeGeometry(shape, { depth: espessura, bevelEnabled: false, curveSegments: 1 });
  // shape no plano (z, y) -> girar para que a extrusão siga +x
  g.rotateY(Math.PI / 2);
  g.translate(x - espessura / 2, 0, 0);
  return g;
}
