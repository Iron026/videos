// Renderizador determinístico: abre a cena no Chromium (WebGL por software), chama quadro(t)
// para cada instante e envia as imagens ao FFmpeg. Uso:
//   node render.mjs --saida video.mp4 [--escala 0.5] [--fps 30] [--inicio 0] [--fim 75]
//   node render.mjs --quadros 1,5.5,12 --pasta ./stills [--escala 0.5]
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const { chromium } = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright');
const arg = (n, d) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : d; };
const RAIZ = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const esc = +arg('escala', 1), W = Math.round(1080 * esc / 2) * 2, H = Math.round(1920 * esc / 2) * 2;
const fps = +arg('fps', 30), ini = +arg('inicio', 0), fim = +arg('fim', 75);
const TIPOS = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => {
  const p = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(RAIZ) || !fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': TIPOS[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(r);
}).listen(0);
const porta = srv.address().port;
const nav = await chromium.launch({ executablePath: fs.existsSync('/opt/pw-browsers/chromium') ? undefined : undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'] });
const pg = await nav.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
pg.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[pagina]', m.text()); });
await pg.goto(`http://127.0.0.1:${porta}/projeto/index.html?w=${W}&h=${H}`);
await pg.waitForFunction(() => window.pronto || window.erro, null, { timeout: 180000 });
const erro = await pg.evaluate(() => window.erro); if (erro) { console.error('ERRO NA CENA:', erro); process.exit(1); }
if (arg('js')) await pg.evaluate(arg('js'));
const foto = async (t) => { await pg.evaluate(t => window.quadro(t), t); return pg.screenshot({ type: 'jpeg', quality: 96 }); };
const quadros = arg('quadros');
if (quadros) {
  const pasta = arg('pasta', 'stills'); fs.mkdirSync(pasta, { recursive: true });
  for (const t of quadros.split(',').map(Number)) { const t0 = Date.now(); fs.writeFileSync(path.join(pasta, `t_${t.toFixed(2).padStart(6, '0')}.jpg`), await foto(t)); console.log('quadro', t, Date.now() - t0, 'ms'); }
} else {
  const saida = arg('saida', 'saida.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', arg('preset', 'medium'), '-crf', arg('crf', '16'), '-pix_fmt', 'yuv420p', '-r', String(fps), saida], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n0 = Math.round(ini * fps), n1 = Math.round(fim * fps); const t0 = Date.now();
  for (let n = n0; n < n1; n++) {
    const img = await foto(n / fps);
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once('drain', r));
    if ((n - n0) % 30 === 0) { const el = (Date.now() - t0) / 1000, feitos = n - n0 + 1; console.log(`quadro ${n}/${n1} t=${(n / fps).toFixed(2)}s  ${(el / feitos).toFixed(2)} s/quadro  restante ~${((n1 - n) * el / feitos / 60).toFixed(1)} min`); }
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await nav.close(); srv.close();
