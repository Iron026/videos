// Benchmark do renderizador em tempo real no Chromium headless (WebGL por software: SwiftShader, sem GPU).
// Uso: node bench.mjs <escala> <n_quadros> <saida_png> [ao=1]
import { createRequire } from 'module'; import { execSync } from 'child_process'; import path from 'path'; import http from 'http'; import fs from 'fs';
const require = createRequire(path.join(execSync('npm root -g').toString().trim(), 'x'));
const { chromium } = require('playwright');
const [escala = '0.5', n = '8', saida = 'rt.png', ao = '1'] = process.argv.slice(2);
const RAIZ = path.resolve('../../..');
const tipos = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.bin': 'application/octet-stream' };
const srv = http.createServer((q, r) => { const f = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': tipos[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
const porta = srv.address().port;
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const W = Math.round(1080 * escala), H = Math.round(1920 * escala);
const p = await b.newPage({ viewport: { width: W, height: H } });
p.on('console', m => { if (m.type() === 'error') console.log('ERRO', m.text()); });
const t0 = Date.now();
await p.goto(`http://127.0.0.1:${porta}/episodio_01_navio_v2/motores/tempo_real/index.html?escala=${escala}&ao=${ao}`);
await p.waitForFunction(() => window.pronto === true, null, { timeout: 600000 });
const carga = (Date.now() - t0) / 1000;
const info = await p.evaluate(() => window.info);
await p.evaluate(() => window.quadro(0));
await p.screenshot({ path: saida });
const tempos = [];
for (let i = 0; i < +n; i++) { const t1 = Date.now(); const ms = await p.evaluate((i) => window.quadro(i), i); tempos.push({ render_ms: ms, total_ms: Date.now() - t1 }); }
const cap0 = Date.now(); await p.screenshot({ path: saida.replace('.png', '_ultimo.png') }); const cap = Date.now() - cap0;
const med = a => a.slice().sort((x, y) => x - y)[Math.floor(a.length / 2)];
console.log(JSON.stringify({ escala: +escala, W, H, ao: ao === '1', info, carga_s: carga, render_mediana_ms: med(tempos.map(t => t.render_ms)), total_mediana_ms: med(tempos.map(t => t.total_ms)), captura_png_ms: cap, tempos }));
await b.close(); srv.close();
