// [Ep. 02 · fork de render_anim.mjs do Ep. 01] Renderiza a sequência de quadros de uma cena animada exportada (exportar_rt2.exportar_atual).
// Uso: node render_anim.mjs "<query>" <pasta_saida> <passo> [inicio] [fim]   (JPEG q95, nome = índice do quadro local)
import { createRequire } from 'module'; import { execSync } from 'child_process'; import path from 'path'; import http from 'http'; import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const [query, saida, passo = '1', ini = '0', fim = '-1'] = process.argv.slice(2);
fs.mkdirSync(saida, { recursive: true });
const RAIZ = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const tipos = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.bin': 'application/octet-stream', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => { const f = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': tipos[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(0);
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const esc = parseFloat((new URLSearchParams(query)).get('escala') || '1');
const p = await b.newPage({ viewport: { width: Math.round(1080 * esc), height: Math.round(1920 * esc) } });
const erros = []; p.on('pageerror', e => erros.push((e.stack || e.message).slice(0, 600)));
await p.goto(`http://127.0.0.1:${srv.address().port}/episodio_02_geladeira/motor/index.html?${query}`);
try { await p.waitForFunction(() => window.pronto === true, null, { timeout: 300000 }); }
catch (e) { console.log('ERRO', erros.join('\n')); process.exit(1); }
const n = await p.evaluate(() => window.nQuadros());
const f1 = +fim < 0 ? n - 1 : Math.min(+fim, n - 1); const t0 = Date.now(); let k = 0;
for (let i = +ini; i <= f1; i += +passo) {
  await p.evaluate((i) => window.quadro(i), i);
  await p.screenshot({ path: path.join(saida, `q${String(i).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 95 }); k++;
  if (k % 20 === 0) console.log(`quadro ${i}/${f1} · ${((Date.now() - t0) / k / 1000).toFixed(2)} s/quadro`);
}
console.log(`FIM ${k} quadros em ${((Date.now() - t0) / 1000).toFixed(1)} s (${((Date.now() - t0) / k / 1000).toFixed(2)} s/quadro)`, erros.length ? 'ERROS ' + erros.join(' | ') : '');
await b.close(); srv.close();
