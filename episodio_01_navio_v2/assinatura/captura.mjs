import { createRequire } from 'module'; import { execSync } from 'child_process'; import path from 'path';
const require = createRequire(path.join(execSync('npm root -g').toString().trim(), 'x'));
const { chromium } = require('playwright');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto('file://' + path.resolve('assinatura.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
await p.screenshot({ path: '../etapa_b/quadros/quadro6_assinatura.png' }); await b.close();
