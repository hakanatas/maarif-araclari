/* Rehber sayfasını A4 PDF'e basar.
 *
 * Kullanım:  node scriptler/07_rehber_pdf.mjs
 * Girdi:     kullanim.html   (önce 05_uygulamalari_uret.py çalıştırılmalı)
 * Çıktı:     Maarif-Arac-Kutusu-Rehberi.pdf
 *
 * Dizgi HTML'in kendi @media print kurallarından gelir; burada yalnız kâğıt
 * boyutu, kenar boşluğu ve sayfa numarası ayarlanır. Yazı tipleri Google
 * Fonts'tan yüklenip PDF'e gömülür, o yüzden ilk çalıştırmada ağ gerekir.
 */
/* playwright depoya bağımlılık olarak eklenmedi; kurulu değilse
   PLAYWRIGHT_PATH ile yolu verilebilir (npm i -D playwright de olur). */
let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  ({ chromium } = await import(process.env.PLAYWRIGHT_PATH
    || '/usr/lib/node_modules/playwright/index.mjs'));
}
import { fileURLToPath } from 'url';
import path from 'path';

const KOK = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const GIRDI = 'file://' + path.join(KOK, 'kullanim.html');
const CIKTI = path.join(KOK, 'Maarif-Arac-Kutusu-Rehberi.pdf');

const tarayici = await chromium.launch();
const sayfa = await tarayici.newPage();
await sayfa.goto(GIRDI, { waitUntil: 'networkidle' });
await sayfa.emulateMedia({ media: 'print', colorScheme: 'light' });
await sayfa.evaluate(() => document.fonts.ready);

const kucuk = 'font-family:-apple-system,Segoe UI,sans-serif;font-size:7.5pt;color:#8A9298;width:100%;padding:0 16mm;';
await sayfa.pdf({
  path: CIKTI,
  format: 'A4',
  printBackground: true,
  margin: { top: '20mm', bottom: '18mm', left: '16mm', right: '16mm' },
  displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate: `<div style="${kucuk}display:flex;justify-content:space-between">
      <span>Maarif Araç Kutusu · Nasıl kullanılır?</span>
      <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
    </div>`,
});

await tarayici.close();
console.log('PDF →', path.relative(KOK, CIKTI));
