// Quadros do plano 4 (assinatura animada): node captura_anim.mjs <pasta> <n_quadros> [ritmo]
import { createRequire } from 'module'; import { execSync } from 'child_process'; import path from 'path'; import fs from 'fs';
const require = createRequire(path.join(execSync('npm root -g').toString().trim(), 'x'));
const { chromium } = require('playwright');
const [saida, n, ritmo] = process.argv.slice(2); fs.mkdirSync(saida, { recursive: true });
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto('file://' + path.resolve('assinatura_anim.html') + (ritmo ? '?ritmo=' + ritmo : '')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
for (let i = 0; i < +n; i++) { await p.evaluate((t) => quadro(t), i / 30); await p.screenshot({ path: path.join(saida, `q${String(i).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 95 }); }
await b.close(); console.log('ok', n);
