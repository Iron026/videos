// Camada 2D desenhada sobre o 3D: rótulos ancorados, cartões, painel, legendas e assinatura.
// Todas as medidas estão em pixels de um quadro 1080×1920 (escaladas para prévias).
const AZUL = '#202B57', BRANCO = '#F6F4EC', AMARELO = '#F3B544', CIANO = '#6FD6F7';
const FONTE = 'Montserrat';
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const suave = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const saida = (x) => 1 - Math.pow(1 - clamp(x, 0, 1), 3);
// opacidade de um elemento visível em [t0, t1] com entrada/saída suaves
export function janela(t, t0, t1, ent = 0.3, sai = 0.3) { return Math.min(saida((t - t0) / ent), saida((t1 - t) / sai)); }

function retRed(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

export class Sobreposicao {
  constructor(canvas, legendas) {
    this.c = canvas; this.ctx = canvas.getContext('2d'); this.leg = legendas;
  }
  iniciar(t) {
    const ctx = this.ctx, s = this.c.width / 1080;
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, this.c.width, this.c.height);
    ctx.setTransform(s, 0, 0, s, 0, 0);
    // vinheta suave
    const g = ctx.createRadialGradient(540, 900, 500, 540, 960, 1250);
    g.addColorStop(0, 'rgba(10,14,35,0)'); g.addColorStop(1, 'rgba(10,14,35,0.38)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920);
  }

  // Rótulo com ponto de ancoragem e linha guia. a = opacidade (0..1); ancora em px (1080×1920).
  rotulo({ texto, ancora, dx = 0, dy = -120, a = 1, cor = AMARELO, tam = 40, ponto = true }) {
    if (a <= 0.001 || !ancora || !ancora.visivel) return;
    const ctx = this.ctx; ctx.save(); ctx.globalAlpha = a;
    const [ax, ay] = [ancora.x, ancora.y];
    ctx.font = `700 ${tam}px ${FONTE}`;
    const linhas = texto.split('\n');
    const w = Math.max(...linhas.map(l => ctx.measureText(l).width)) + 56, h = linhas.length * tam * 1.22 + 30;
    let bx = clamp(ax + dx - w / 2, 40, 920 - w), by = clamp(ay + dy - h / 2, 140, 1180 - h);
    const esc = 0.85 + 0.15 * a;
    // linha guia
    if (ponto) {
      ctx.strokeStyle = cor; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(ax, ay);
      const cx = clamp(ax, bx + 20, bx + w - 20), cy = ay < by ? by : (ay > by + h ? by + h : by + h / 2);
      ctx.lineTo(cx, cy); ctx.stroke();
      ctx.fillStyle = BRANCO; ctx.beginPath(); ctx.arc(ax, ay, 11, 0, 7); ctx.fill();
      ctx.fillStyle = cor; ctx.beginPath(); ctx.arc(ax, ay, 7, 0, 7); ctx.fill();
    }
    ctx.translate(bx + w / 2, by + h / 2); ctx.scale(esc, esc); ctx.translate(-(bx + w / 2), -(by + h / 2));
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 6;
    retRed(ctx, bx, by, w, h, 22); ctx.fillStyle = 'rgba(32,43,87,0.92)'; ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.lineWidth = 3; ctx.strokeStyle = cor; ctx.stroke();
    ctx.fillStyle = BRANCO; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    linhas.forEach((l, i) => ctx.fillText(l, bx + w / 2, by + 15 + tam * 0.61 + i * tam * 1.22));
    ctx.restore();
  }

  // Cartão superior com destaque em palavras entre *asteriscos*.
  cartao({ texto, a = 1, y = 250, tam = 52 }) {
    if (a <= 0.001) return;
    const ctx = this.ctx; ctx.save(); ctx.globalAlpha = a;
    ctx.font = `800 ${tam}px ${FONTE}`;
    const linhas = texto.split('\n');
    const larg = (l) => ctx.measureText(l.replace(/\*/g, '')).width;
    const w = Math.min(980, Math.max(...linhas.map(larg)) + 80), h = linhas.length * tam * 1.25 + 44;
    const x = 540 - w / 2, yy = y - 18 * (1 - a);
    ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8;
    retRed(ctx, x, yy, w, h, 28); ctx.fillStyle = 'rgba(32,43,87,0.94)'; ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.fillStyle = AMARELO; retRed(ctx, x, yy + h - 10, w, 10, 5); ctx.fill();
    ctx.textBaseline = 'middle';
    linhas.forEach((l, i) => {
      const partes = l.split('*'); let cx = 540 - larg(l) / 2; const cy = yy + 22 + tam * 0.66 + i * tam * 1.25;
      partes.forEach((p, j) => { ctx.fillStyle = j % 2 ? AMARELO : BRANCO; ctx.textAlign = 'left'; ctx.fillText(p, cx, cy); cx += ctx.measureText(p).width; });
    });
    ctx.restore();
  }

  // Painel comparando densidades (Cena 03).
  painelDensidade(a, prog) {
    if (a <= 0.001) return;
    const ctx = this.ctx; ctx.save(); ctx.globalAlpha = a;
    const x = 90, y = 200, w = 820, h = 330;
    ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 26; ctx.shadowOffsetY = 8;
    retRed(ctx, x, y, w, h, 28); ctx.fillStyle = 'rgba(32,43,87,0.94)'; ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.fillStyle = BRANCO; ctx.font = `800 40px ${FONTE}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText('Massa de 1 m³', x + 40, y + 56);
    const barra = (rot, val, txt, cor, yy, frac) => {
      ctx.font = `700 34px ${FONTE}`; ctx.fillStyle = BRANCO; ctx.fillText(rot, x + 40, yy);
      const bw = 480 * frac * saida(prog);
      ctx.fillStyle = 'rgba(246,244,236,0.12)'; retRed(ctx, x + 300, yy - 26, 480, 52, 14); ctx.fill();
      ctx.fillStyle = cor; retRed(ctx, x + 300, yy - 26, Math.max(bw, 28), 52, 14); ctx.fill();
      ctx.font = `800 32px ${FONTE}`; ctx.fillStyle = AZUL; ctx.textAlign = 'right';
      if (bw > 170) ctx.fillText(txt, x + 300 + bw - 18, yy + 2); else { ctx.fillStyle = BRANCO; ctx.textAlign = 'left'; ctx.fillText(txt, x + 300 + Math.max(bw, 28) + 16, yy + 2); }
      ctx.textAlign = 'left';
    };
    barra('Aço', 7.85, '≈ 7,85 t', AMARELO, y + 145, 1.0);
    barra('Água do mar', 1.03, '≈ 1,03 t', CIANO, y + 240, 1.03 / 7.85);
    ctx.restore();
  }

  legenda(t) {
    const ctx = this.ctx; const l = this.leg.find(x => t >= x.inicio - 0.05 && t <= x.fim);
    if (!l) return;
    const a = saida((t - l.inicio + 0.05) / 0.12);
    ctx.save(); ctx.globalAlpha = Math.min(1, a + 0.0);
    const tam = 60; ctx.font = `800 ${tam}px ${FONTE}`; ctx.textBaseline = 'alphabetic';
    // quebra em até 2 linhas, largura máx. 820 px
    const pal = l.palavras; const linhas = [[]]; let largura = 0; const esp = ctx.measureText(' ').width;
    for (const p of pal) {
      const w = ctx.measureText(p.palavra).width;
      if (largura + w > 820 && linhas[linhas.length - 1].length) { linhas.push([]); largura = 0; }
      linhas[linhas.length - 1].push({ ...p, w }); largura += w + esp;
    }
    const cx = 515, baseY = 1335 - (linhas.length - 1) * tam * 1.18;
    const esc = 0.94 + 0.06 * a; ctx.translate(cx, baseY); ctx.scale(esc, esc); ctx.translate(-cx, -baseY);
    linhas.forEach((ln, i) => {
      const total = ln.reduce((s, p) => s + p.w, 0) + esp * (ln.length - 1);
      let x = cx - total / 2; const y = baseY + i * tam * 1.18;
      for (const p of ln) {
        const ativo = t >= p.inicio - 0.03;
        ctx.lineJoin = 'round'; ctx.lineWidth = 14; ctx.strokeStyle = 'rgba(13,19,48,0.92)'; ctx.strokeText(p.palavra, x, y);
        ctx.fillStyle = ativo ? (t <= p.fim + 0.05 ? AMARELO : BRANCO) : 'rgba(246,244,236,0.55)';
        ctx.fillText(p.palavra, x, y); x += p.w + esp;
      }
    });
    ctx.restore();
  }

  mergulho(a) { // transição na cor da marca
    if (a <= 0.001) return; const ctx = this.ctx; ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = AZUL; ctx.fillRect(0, 0, 1080, 1920); ctx.restore();
  }

  assinatura(t, t0) {
    const p = t - t0; if (p < 0) return;
    const ctx = this.ctx; ctx.save();
    ctx.globalAlpha = saida(p / 0.45);
    const g = ctx.createLinearGradient(0, 0, 0, 1920); g.addColorStop(0, '#26336a'); g.addColorStop(1, '#151d40');
    ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920);
    // olho estilizado: contorno desenhado progressivamente, íris e pupila
    const cx = 540, cy = 760, lw = 330, lh = 150;
    const d = saida((p - 0.15) / 0.8);
    ctx.globalAlpha = 1; ctx.lineWidth = 16; ctx.lineCap = 'round'; ctx.strokeStyle = BRANCO;
    const curva = (sinal) => { ctx.beginPath(); ctx.moveTo(cx - lw, cy); ctx.bezierCurveTo(cx - lw * 0.45, cy + sinal * lh * 1.25, cx + lw * 0.45, cy + sinal * lh * 1.25, cx + lw, cy); ctx.stroke(); };
    ctx.save(); ctx.beginPath(); ctx.rect(cx - lw - 20, 0, (2 * lw + 40) * d, 1920); ctx.clip(); curva(-1); curva(1); ctx.restore();
    const ir = saida((p - 0.55) / 0.5);
    if (ir > 0) {
      ctx.fillStyle = AMARELO; ctx.beginPath(); ctx.arc(cx, cy, 92 * ir, 0, 7); ctx.fill();
      ctx.fillStyle = AZUL; ctx.beginPath(); ctx.arc(cx, cy, 46 * ir, 0, 7); ctx.fill();
      ctx.fillStyle = BRANCO; ctx.beginPath(); ctx.arc(cx + 26 * ir, cy - 28 * ir, 14 * ir, 0, 7); ctx.fill();
    }
    const tt = saida((p - 0.4) / 0.5);
    ctx.globalAlpha = tt; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = BRANCO; ctx.font = `900 84px ${FONTE}`; ctx.fillText('De Olho no Invisível', cx, 1070 + 20 * (1 - tt));
    const ts = saida((p - 2.0) / 0.5);
    ctx.globalAlpha = ts; ctx.fillStyle = AMARELO; ctx.font = `700 50px ${FONTE}`; ctx.fillText('O invisível ganha forma.', cx, 1160 + 16 * (1 - ts));
    ctx.globalAlpha = tt * 0.75; ctx.fillStyle = BRANCO; ctx.font = `600 34px ${FONTE}`; ctx.fillText('@deolhonoinvisivel', cx, 1260);
    ctx.restore();
  }
}
