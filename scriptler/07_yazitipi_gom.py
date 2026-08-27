#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rehber sayfasının yazı tiplerini indirip gömülebilir CSS'e çevirir.

Kullanım:  python3 scriptler/07_yazitipi_gom.py
Çıktı:     scriptler/sablonlar/yazitipleri.css   (base64 gömülü @font-face blokları)

Neden: sayfa "internet bile gerekmiyor" diyor ama Google Fonts'a bağlanıyordu.
Ayrıca PDF'e basarken tarayıcı yazı tiplerini çekemeyince dizgi yedek yüzlere
düşüyor. Yalnız latin ve latin-ext alt kümeleri alınır (Türkçe harfler latin-ext'te).
Bu script bir kez çalıştırılır; ürettiği CSS depoya işlenir, sonraki derlemeler ağ istemez.
"""
import base64, os, re, subprocess, sys
from urllib.parse import quote

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIKTI = os.path.join(KOK, 'scriptler', 'sablonlar', 'yazitipleri.css')
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/125.0 Safari/537.36')

# Gövde yüzleri tam alt kümeyle gömülür. Yalnız rehber sayfasının kullandığı
# ağırlıklar alınır; araçlar bu dosyayı kullanmıyor (onlar Google Fonts'a bağlı).
ISTEK = ('https://fonts.googleapis.com/css2?'
         'family=IBM+Plex+Mono:wght@500'
         '&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap')
ALT_KUMELER = {'latin', 'latin-ext'}

# Başlık yüzü yalnız birkaç satırda kullanılıyor; tam alt küme 210 KB tutuyordu.
# Türkçe alfabe + rakam + noktalama ile sınırlayınca onda birine iniyor.
# Başlıklarda bu kümenin dışında bir karakter kullanılırsa yedek yüze düşer —
# yeni bir işaret eklerseniz ALFABE'ye de ekleyip bu scripti yeniden çalıştırın.
ALFABE = ('ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZQWX'
          'abcçdefgğhıijklmnoöprsştuüvyzqwx'
          '0123456789 .,;:!?\'\u2019\u201c\u201d()[]{}-\u2013\u2014/&%@#*+=<>\u2026\u00b7\u2192\u21c4')
BASLIK_ISTEK = ('https://fonts.googleapis.com/css2?'
                'family=Bricolage+Grotesque:opsz,wght@12..96,600&display=swap'
                '&text=' + quote(ALFABE, safe=''))


def getir(url, ikili=False):
    c = subprocess.run(['curl', '-sL', '--max-time', '60', '-A', UA, url],
                       capture_output=True)
    if c.returncode or not c.stdout:
        sys.exit('indirilemedi: ' + url)
    return c.stdout if ikili else c.stdout.decode('utf-8')


def main():
    css = getir(ISTEK)
    bloklar = [(alt, blok) for alt, blok in
               re.findall(r'/\*\s*([a-z-]+)\s*\*/\s*(@font-face\s*\{.*?\})', css, re.S)
               if alt in ALT_KUMELER]
    # text= ile daraltılan istek alt küme yorumu içermez; blokları doğrudan al
    bloklar += [('başlık', b) for b in re.findall(r'@font-face\s*\{.*?\}', getir(BASLIK_ISTEK), re.S)]
    if not bloklar:
        sys.exit('yazı tipi bloğu ayrıştırılamadı')

    parcalar, toplam = [], 0
    for alt, blok in bloklar:
        # text= ile daraltılmış istekte kaynak .woff2 uzantısı taşımaz (…/l/font?kit=…)
        m = re.search(r"url\((https://[^)]+)\)", blok)
        if not m:
            continue
        veri = getir(m.group(1), ikili=True)
        toplam += len(veri)
        b64 = base64.b64encode(veri).decode('ascii')
        parcalar.append(re.sub(r"url\(https://[^)]+\)",
                               "url(data:font/woff2;base64," + b64 + ")", blok, count=1))
        ad = re.search(r"font-family:\s*'([^']+)'", blok)
        agirlik = re.search(r'font-weight:\s*([^;]+);', blok)
        print('%-22s %-10s %-10s %6.1f KB' % (ad.group(1) if ad else '?', alt,
                                              (agirlik.group(1).strip() if agirlik else ''),
                                              len(veri) / 1024))

    if not parcalar:
        sys.exit('gömülecek yüz bulunamadı')
    basli = ('/* Otomatik üretildi: scriptler/07_yazitipi_gom.py\n'
             '   Kaynak: Google Fonts (Bricolage Grotesque, IBM Plex Sans, IBM Plex Mono —\n'
             '   hepsi SIL Open Font License). Yalnız latin ve latin-ext alt kümeleri gömüldü.\n'
             '   Sayfanın çevrimdışı çalışması ve PDF dizgisinin doğru yüzlerle basılması için. */\n')
    with open(CIKTI, 'w', encoding='utf-8') as f:
        f.write(basli + '\n'.join(parcalar) + '\n')
    print('\n%s → %.0f KB yazı tipi, %.0f KB dosya'
          % (os.path.relpath(CIKTI, KOK), toplam / 1024, os.path.getsize(CIKTI) / 1024))


if __name__ == '__main__':
    main()
