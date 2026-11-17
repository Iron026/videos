// Benchmark do motor em tempo real v2 (Chromium headless, WebGL por software — sem GPU).
// Uso: node bench2.mjs "<query>" <n_quadros> <saida_png>     ex.: "cena=../cena2_q3/&escala=1&ao=1"
import { createRequire } from 'module'; import { execSync } from 'child_process'; import path from 'path'; import http from 'http'; import fs from 'fs';
const require = createRequire(path.join(execSync('npm root -g').toString().trim(), 'x'));
const { chromium } = require('playwright');
const [query = 'escala=0.5', n = '4', saida = 'rt2.png'] = process.argv.slice(2);
const RAIZ = path.resolve('../../..');
const tipos = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.bin': 'application/octet-stream', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => { const f = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': tipos[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
const porta = srv.address().port;
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const esc = parseFloat((new URLSearchParams(query)).get('escala') || '0.5');
const p = await b.newPage({ viewport: { width: Math.round(1080 * esc), height: Math.round(1920 * esc) } });
const erros = []; p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') erros.push(m.text().slice(0, 400)); });
p.on('pageerror', e => erros.push('PAGEERROR ' + (e.stack || e.message).slice(0, 900)));
const t0 = Date.now();
await p.goto(`http://127.0.0.1:${porta}/episodio_01_navio_v2/motores/tempo_real_v2/index.html?${query}`);
try { await p.waitForFunction(() => window.pronto === true, null, { timeout: 300000 }); }
catch (e) { console.log(JSON.stringify({ erro: 'timeout', erros })); process.exit(1); }
const carga = (Date.now() - t0) / 1000;
const info = await p.evaluate(() => window.info);
await p.evaluate(() => window.quadro(0)); await p.screenshot({ path: saida });
const tempos = [];
for (let i = 0; i < +n; i++) tempos.push(await p.evaluate((i) => window.quadro(i), i));
await p.screenshot({ path: saida.replace('.png', '_ultimo.png') });
const med = a => a.slice().sort((x, y) => x - y)[Math.floor(a.length / 2)];
console.log(JSON.stringify({ query, info, carga_s: carga, render_mediana_ms: med(tempos), primeiro_ms: tempos[0], tempos_ms: tempos, erros: erros.slice(0, 6) }));
await b.close(); srv.close();
