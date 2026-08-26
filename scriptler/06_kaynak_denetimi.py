#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veri tazeliği: sürüm damgası üretir ve resmî kaynakların değişip değişmediğini denetler.

Kullanım:
  python3 scriptler/06_kaynak_denetimi.py            # yerel denetim + veri/surum.json
  python3 scriptler/06_kaynak_denetimi.py --uzak     # ayrıca tymm.meb.gov.tr'yi sorgular
  python3 scriptler/06_kaynak_denetimi.py --uzak --kaydet   # bulunanı yeni ölçüt olarak yazar

Çıktı:  veri/surum.json           araçların altbilgisinde gösterilen üretim damgası
        veri/kaynak-imzalari.json her kaynağın parmak izi (yerel özet + uzak başlıklar)

Uzak denetim PDF'i indirmez; yalnız HTTP başlıklarına (etag, last-modified, content-length)
bakar. Bu üçünden biri değişmişse belge güncellenmiş demektir: 00→05 adımları yeniden
çalıştırılmalıdır. Çıkış kodu değişiklik varsa 1'dir (zamanlanmış denetime uygundur).
"""
import hashlib, json, os, subprocess, sys
from datetime import date

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = os.path.join(KOK, 'veri')
KAYNAK = os.path.join(KOK, 'kaynak')
IMZA_YOLU = os.path.join(VERI, 'kaynak-imzalari.json')
SURUM_YOLU = os.path.join(VERI, 'surum.json')

sys.path.insert(0, os.path.join(KOK, 'scriptler'))
_indir = __import__('00_kaynaklari_indir')
KOK_URL = _indir.KOK_URL
PROGRAMLAR = _indir.PROGRAMLAR
BECERI_SAYFALARI = _indir.BECERI_SAYFALARI


def ozet(yol):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for p in iter(lambda: f.read(1 << 16), b''):
            h.update(p)
    return h.hexdigest()[:16]


def yerel_imzalar():
    """Ayrıştırıcıların gerçekten okuduğu dosyaların (metne çevrilmiş PDF'ler) özeti."""
    d = {}
    metin = os.path.join(KAYNAK, 'metin')
    for ad in sorted(PROGRAMLAR):
        yol = os.path.join(metin, ad + '.txt')
        d[ad] = {'yol': 'kaynak/metin/%s.txt' % ad, 'url': KOK_URL + PROGRAMLAR[ad]}
        if os.path.exists(yol):
            d[ad]['ozet'] = ozet(yol)
            d[ad]['boyut'] = os.path.getsize(yol)
        else:
            d[ad]['ozet'] = None
    return d


def uzak_basliklar(url, sure=25):
    try:
        c = subprocess.run(['curl', '-sIL', '--max-time', str(sure), url],
                           capture_output=True, text=True, timeout=sure + 5)
    except Exception as e:
        return {'hata': str(e)}
    b = {}
    for satir in c.stdout.splitlines():
        if ':' not in satir:
            continue
        k, v = satir.split(':', 1)
        k = k.strip().lower()
        if k in ('etag', 'last-modified', 'content-length'):
            b[k] = v.strip()
    return b or {'hata': 'başlık alınamadı'}


def kayitlar():
    """Araçlara gömülen veri setlerinin büyüklüğü — damgada gösterilir."""
    def n(ad, anahtar=None):
        try:
            with open(os.path.join(VERI, ad), encoding='utf-8') as f:
                v = json.load(f)
            return len(v[anahtar] if anahtar else v)
        except Exception:
            return None
    def bag(ad):
        """Köprü dosyaları çıktı/tema anahtarlıdır; sayılan, kurulan ders bağlarıdır."""
        try:
            with open(os.path.join(VERI, ad), encoding='utf-8') as f:
                return sum(len(v.get('kopru', {})) for v in json.load(f).values())
        except Exception:
            return None
    return {'beceri kodu': n('beceriler.json'),
            'öğrenme çıktısı': n('ogrenme-ciktilari.json'),
            'tema': n('temalar.json'),
            'çıktı düzeyi köprü': bag('cikti-duzeyi-kopruler.json'),
            'tema düzeyi köprü': bag('tema-duzeyi-kopruler.json')}


def main():
    uzak = '--uzak' in sys.argv
    kaydet = '--kaydet' in sys.argv

    eski = {}
    if os.path.exists(IMZA_YOLU):
        with open(IMZA_YOLU, encoding='utf-8') as f:
            eski = json.load(f).get('kaynaklar', {})

    yeni = yerel_imzalar()
    degisen, eksik, yeni_kaynak = [], [], []

    for ad, bilgi in yeni.items():
        e = eski.get(ad)
        if bilgi['ozet'] is None:
            eksik.append(ad)
        if e is None:
            yeni_kaynak.append(ad)
        elif bilgi['ozet'] and e.get('ozet') and bilgi['ozet'] != e['ozet']:
            degisen.append('%s  (yerel metin değişmiş)' % ad)

    if uzak:
        print('Uzak denetim: %d belge sorgulanıyor…' % len(yeni), file=sys.stderr)
        for ad, bilgi in yeni.items():
            b = uzak_basliklar(bilgi['url'])
            bilgi['uzak'] = b
            e = (eski.get(ad) or {}).get('uzak') or {}
            if 'hata' in b:
                print('  ! %-52s %s' % (ad, b['hata']), file=sys.stderr)
                continue
            for alan in ('etag', 'last-modified', 'content-length'):
                if e.get(alan) and b.get(alan) and e[alan] != b[alan]:
                    degisen.append('%s  (%s: %s → %s)' % (ad, alan, e[alan], b[alan]))
                    break
        for ad, yol in BECERI_SAYFALARI:
            yeni.setdefault('beceri:' + ad, {})['url'] = KOK_URL + yol

    bugun = date.today().isoformat()
    if kaydet or not eski:
        with open(IMZA_YOLU, 'w', encoding='utf-8') as f:
            json.dump({'tarih': bugun, 'kaynaklar': yeni}, f, ensure_ascii=False, indent=1)
        print('Ölçüt yazıldı → veri/kaynak-imzalari.json')

    with open(SURUM_YOLU, 'w', encoding='utf-8') as f:
        json.dump({'uretim': bugun,
                   'kaynak': KOK_URL,
                   'belge': len([1 for v in yeni.values() if v.get('ozet')]),
                   'kayitlar': kayitlar()}, f, ensure_ascii=False, indent=1)
    print('Sürüm damgası → veri/surum.json  (%s)' % bugun)

    if eksik:
        print('\nMetni bulunamayan kaynak (%d): önce 00_kaynaklari_indir.py' % len(eksik))
        for a in eksik:
            print('  -', a)
    if degisen:
        print('\nDEĞİŞMİŞ KAYNAK (%d) — veriyi yeniden üretin:' % len(degisen))
        for a in degisen:
            print('  *', a)
        sys.exit(1)
    if not eksik:
        print('\nDeğişiklik yok; veri güncel.')


if __name__ == '__main__':
    main()
