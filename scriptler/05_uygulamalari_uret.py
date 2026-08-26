#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Şablonlara veri gömerek araclar/ altındaki yayına hazır HTML dosyalarını üretir.

Kullanım:  python3 scriptler/05_uygulamalari_uret.py
Girdi:     scriptler/sablonlar/*.sablon.html  +  veri/*.json
Çıktı:     araclar/*.html   (tek dosya, bağımsız çalışır, kurulum gerektirmez)
"""
import json, os, re, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SABLON = os.path.join(KOK, 'scriptler', 'sablonlar')
VERI = os.path.join(KOK, 'veri')
CIKTI = os.path.join(KOK, 'araclar')

ARACLAR = [
    ('kod-pusulasi', 'Kod Pusulası', '🧭',
     'TYMM beceri, değer ve eğilim kodlarının aranabilir sözlüğü'),
    ('kazanim-gezgini', 'Kazanım Gezgini', '🗺️',
     '15 ortaokul programındaki 1256 öğrenme çıktısı tek arayüzde'),
    ('ders-plani', 'Ders Planı Atölyesi', '📋',
     'Tema seçince resmî metinle dolan, düzenlenebilir ve yazdırılabilir ders planı'),
    ('disiplinler-haritasi', 'Disiplinler Arası Harita', '🕸️',
     'Derslerin köprü ağı, köprüyü doğuran çıktılar ve program alıntıları'),
    ('beceri-panosu', 'Beceri Gelişim Panosu', '📊',
     'Öğrenci × süreç bileşeni izleme matrisi; verisi tarayıcıda kalır, yedeklenebilir'),
]


def oku(ad):
    with open(os.path.join(VERI, ad), encoding='utf-8') as f:
        return json.load(f)


def kod_sozlugu(beceriler, kirp=180):
    return {e['code']: {'n': e['name'],
                        'd': e['def'][:kirp] + ('…' if len(e['def']) > kirp else '')}
            for e in beceriler}


def veri_hazirla():
    beceriler = oku('beceriler.json')
    ciktilar = oku('ogrenme-ciktilari.json')
    return {
        'kod-pusulasi': {'entries': beceriler, 'usage': oku('beceri-kullanim.json')},
        'kazanim-gezgini': {'ciktilar': ciktilar, 'kodlar': kod_sozlugu(beceriler, 220)},
        'ders-plani': {'temalar': oku('temalar.json'),
                       'ciktilar': [{'ders': c['ders'], 'code': c['code'],
                                     'statement': c['statement'], 'sb': c['sb']} for c in ciktilar],
                       'kodlar': kod_sozlugu(beceriler)},
        'disiplinler-haritasi': oku('harita.json'),
        'beceri-panosu': {'ciktilar': [{'ders': c['ders'], 'sinif': c['sinif'], 'temaNo': c['temaNo'],
                                        'tema': c['tema'], 'code': c['code'],
                                        'statement': c['statement'], 'sb': c['sb']}
                                       for c in ciktilar if c['sb']]},
    }


def nav(aktif):
    ogeler = []
    for slug, ad, ikon, _ in ARACLAR:
        if slug == aktif:
            ogeler.append(f'<span class="nav-oge etkin" aria-current="page">{ikon} {ad}</span>')
        else:
            ogeler.append(f'<a class="nav-oge" href="./{slug}.html">{ikon} {ad}</a>')
    return ('<nav class="site-nav" aria-label="Araçlar">'
            '<a class="nav-oge nav-ev" href="../index.html">← Maarif Araç Kutusu</a>'
            + ''.join(ogeler) + '</nav>')




ORTAK_JS = """<script>
/* Araçlar arası ortak URL durumu.
   Her araç seçimini adres çubuğuna yazar; böylece bağlantı paylaşılabilir,
   yer imine eklenebilir ve araçlar birbirine seçim taşıyabilir. */
window.URLD = {
  oku() { return Object.fromEntries(new URLSearchParams(location.search)); },
  yaz(obj) {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(obj)) if (v !== '' && v != null) p.set(k, v);
    const s = p.toString();
    history.replaceState(null, '', s ? location.pathname + '?' + s : location.pathname);
  },
  bag(dosya, obj) {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(obj || {})) if (v !== '' && v != null) p.set(k, v);
    const s = p.toString();
    return './' + dosya + (s ? '?' + s : '');
  }
};
</script>
"""

NAV_CSS = """
  .site-nav {
    display: flex; flex-wrap: wrap; gap: 0.3rem; align-items: center;
    padding: 0.5rem 1.2rem; border-bottom: 1px solid var(--line);
    background: var(--surface); font-size: 0.82rem;
  }
  .site-nav .nav-oge {
    color: var(--ink-soft); text-decoration: none; padding: 0.25rem 0.6rem;
    border-radius: 99px; border: 1px solid transparent; white-space: nowrap;
  }
  .site-nav a.nav-oge:hover, .site-nav a.nav-oge:focus-visible {
    border-color: var(--line); color: var(--ink); outline: none;
  }
  .site-nav .etkin { color: var(--petrol); font-weight: 600; }
  .site-nav .nav-ev { margin-right: auto; font-weight: 600; color: var(--petrol); }
  @media print { .site-nav { display: none; } }
"""


AY = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran',
      'Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']


def tarih_tr(iso):
    try:
        y, a, g = (int(x) for x in iso.split('-'))
        return '%d %s %d' % (g, AY[a - 1], y)
    except Exception:
        return iso


def damga_html():
    """Her sayfanın altbilgisine düşen veri sürümü damgası.

    Statik bir site kendi güncelliğini bilemez; okuyucunun elindeki verinin ne zaman
    hangi kaynaktan üretildiğini görmesi bu yüzden önemli. Damga veri/surum.json'dan
    gelir; o dosyayı 06_kaynak_denetimi.py yazar.
    """
    yol = os.path.join(VERI, 'surum.json')
    if not os.path.exists(yol):
        return ''
    with open(yol, encoding='utf-8') as f:
        s = json.load(f)
    sayilar = ' · '.join('%s %s' % (f'{v:,}'.replace(',', '.'), k)
                         for k, v in (s.get('kayitlar') or {}).items() if v)
    return ('<p class="veri-damgasi">'
            f'<b>Veri sürümü: {tarih_tr(s.get("uretim", ""))}</b> — '
            f'{s.get("belge", 0)} resmî belgeden otomatik üretildi. {sayilar}. '
            'Resmî belgeler güncellenmiş olabilir; bağlayıcı olan '
            f'<a href="{s.get("kaynak", "https://tymm.meb.gov.tr")}">kaynaktaki</a> son sürümdür.'
            '</p>')


DAMGA_CSS = """
  .veri-damgasi {
    margin-top: 0.9rem; padding-top: 0.7rem; border-top: 1px solid var(--line);
    font-size: 0.74rem; line-height: 1.6; color: var(--ink-faint);
  }
  .veri-damgasi b { color: var(--ink-soft); font-weight: 600; }
"""


def favicon(emoji):
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
           "<text y='.9em' font-size='90'>" + emoji + "</text></svg>")
    from urllib.parse import quote
    return "data:image/svg+xml," + quote(svg)


def uret(slug, ad, ikon, aciklama, veri):
    yol = os.path.join(SABLON, slug + '.sablon.html')
    with open(yol, encoding='utf-8') as f:
        sablon = f.read()

    gomulu = json.dumps(veri, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    if '{/*DATA*/}' not in sablon:
        sys.exit('HATA: {/*DATA*/} yer tutucusu yok → ' + yol)
    govde = sablon.replace('{/*DATA*/}', gomulu)

    # şablon <title> + <link> + <style> ile başlar; ilk </style> sonrası gövdedir
    kesim = govde.find('</style>')
    if kesim < 0:
        sys.exit('HATA: </style> bulunamadı → ' + yol)
    kesim += len('</style>')
    bas, kalan = govde[:kesim], govde[kesim:]

    # nav stilini <style> bloğunun sonuna ekle
    bas = bas[:bas.rfind('</style>')] + NAV_CSS + DAMGA_CSS + '</style>'

    # veri sürümü damgasını son altbilginin içine yerleştir
    damga = damga_html()
    if damga:
        kes = kalan.rfind('</footer>')
        if kes < 0:
            sys.exit('HATA: </footer> bulunamadı → ' + yol)
        kalan = kalan[:kes] + damga + kalan[kes:]

    baslik = re.search(r'<title>(.*?)</title>', bas, re.S)
    baslik = baslik.group(1).strip() if baslik else ad

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{aciklama}">
<link rel="icon" href="{favicon(ikon)}">
{bas}
</head>
<body>
{ORTAK_JS}
{nav(slug)}
{kalan.strip()}
</body>
</html>
"""
    hedef = os.path.join(CIKTI, slug + '.html')
    os.makedirs(CIKTI, exist_ok=True)
    with open(hedef, 'w', encoding='utf-8') as f:
        f.write(html)
    return hedef, len(html)


def index_damgala():
    """Açılış sayfası elle yazılıyor; damgası her derlemede yer tutucuya basılır."""
    yol = os.path.join(KOK, 'index.html')
    if not os.path.exists(yol):
        return
    with open(yol, encoding='utf-8') as f:
        s = f.read()
    damga = damga_html()
    if not damga:
        return
    if '<!--DAMGA-->' not in s:
        print('UYARI: index.html içinde <!--DAMGA--> yer tutucusu yok; damga basılmadı')
        return
    yeni_s = re.sub(r'<!--DAMGA-->.*?<!--/DAMGA-->|<!--DAMGA-->',
                    '<!--DAMGA-->' + damga + '<!--/DAMGA-->', s, count=1, flags=re.S)
    if yeni_s != s:
        with open(yol, 'w', encoding='utf-8') as f:
            f.write(yeni_s)
    print(f'{"Açılış sayfası damgası":26} → index.html')


def main():
    veriler = veri_hazirla()
    for slug, ad, ikon, aciklama in ARACLAR:
        hedef, n = uret(slug, ad, ikon, aciklama, veriler[slug])
        print(f'{ad:26} → {os.path.relpath(hedef, KOK):38} {n/1024:8.0f} KB')
    index_damgala()


if __name__ == '__main__':
    main()
