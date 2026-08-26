#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Öğrenme çıktısı düzeyinde disiplinler arası köprüleri çıkarır.

Yöntem: her tema bloğu, içindeki öğrenme çıktısı kodlarının konumlarına göre
segmentlere bölünür; bir segmentte geçen ders adları o çıktıya ait köprü sayılır.
Kanıt olarak metinden cümle alıntısı saklanır.
"""
import re, json, os
from collections import defaultdict

import os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'kaynak')
VERI = os.path.join(KOK, 'veri')
os.makedirs(VERI, exist_ok=True)
DIR = os.path.join(KAYNAK, 'metin')

# (dosya, ders adı, tam kod deseni, kısa kod deseni)
PROGRAMLAR = [
 ('Turkce_5-8_Ogretim_Programi', 'Türkçe', r'T\.[DOKY]\.[1-8]\.\d{1,2}', None),
 ('Matematik_5-8_Ogretim_Programi', 'Matematik', r'MAT\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Fen_Bilimleri_3-8_Ogretim_Programi', 'Fen Bilimleri', r'FB\.[1-8]\.\d{1,2}\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}\.\d{1,2}'),
 ('Sosyal_Bilgiler_4-7_Ogretim_Programi', 'Sosyal Bilgiler', r'SB\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Din_Kulturu_ve_Ahlak_Bilgisi_4-8_Ogretim_Programi', 'Din Kültürü ve Ahlak Bilgisi', r'DKAB\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('TC_Inkilap_Tarihi_ve_Ataturkculuk_8_Ogretim_Programi', 'T.C. İnkılap Tarihi ve Atatürkçülük', r'İTA\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Bilisim_Teknolojileri_ve_Yazilim_Ogretim_Programi', 'Bilişim Teknolojileri ve Yazılım', r'BTY\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Teknoloji_ve_Tasarim_7-8_Ogretim_Programi', 'Teknoloji ve Tasarım', r'TT\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Beden_Egitimi_ve_Spor_Ogretim_Programi', 'Beden Eğitimi ve Spor', r'BES\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Gorsel_Sanatlar_Ogretim_Programi', 'Görsel Sanatlar', r'GS\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Muzik_Ogretim_Programi', 'Müzik', r'MÜZ\.[1-8]\.\d{1,2}\.\d{1,2}', r'[1-8]\.\d{1,2}\.\d{1,2}'),
 ('Secmeli_Gorgu_Kurallari_ve_Nezaket_Ogretim_Programi', 'Görgü Kuralları ve Nezaket (Seçmeli)', r'GKN\.[1-3]\.\d{1,2}\.\d{1,2}', None),
 ('Secmeli_Masal_ve_Destanlarimiz_Ogretim_Programi', 'Masal ve Destanlarımız (Seçmeli)', r'MD\.[1-3]\.\d{1,2}\.\d{1,2}', None),
 ('Secmeli_Yazarlik_ve_Yazma_Becerileri_Ogretim_Programi', 'Yazarlık ve Yazma Becerileri (Seçmeli)', r'YYB\.[1-3]\.\d{1,2}\.\d{1,2}', None),
 ('Secmeli_Okuma_Becerileri_Ogretim_Programi', 'Okuma Becerileri (Seçmeli)', r'OB\.\d{1,2}\.\d{1,2}', None),
]

# ders adı kalıpları (küçük harfe indirgenmiş metinde aranır)
DERS_KALIP = [
 ('Türkçe', r'türkçe'),
 ('Matematik', r'matematik'),
 ('Fen Bilimleri', r'fen bilimleri'),
 ('Sosyal Bilgiler', r'sosyal bilgiler'),
 ('Din Kültürü ve Ahlak Bilgisi', r'din kültürü'),
 ('T.C. İnkılap Tarihi ve Atatürkçülük', r'i̇nkılap tarihi|inkılap tarihi'),
 ('Bilişim Teknolojileri ve Yazılım', r'bilişim teknolojileri'),
 ('Teknoloji ve Tasarım', r'teknoloji ve tasarım'),
 ('Beden Eğitimi ve Spor', r'beden eğitimi'),
 ('Görsel Sanatlar', r'görsel sanatlar'),
 ('Müzik', r'müzik'),
 ('Hayat Bilgisi', r'hayat bilgisi'),
 ('İngilizce', r'i̇ngilizce|ingilizce|yabancı dil'),
 ('Trafik Güvenliği', r'trafik güvenliği'),
 ('İnsan Hakları ve Vatandaşlık', r'vatandaşlık ve demokrasi'),
]
# "ders" bağlamı: ders adının yakınında bu sözcüklerden biri geçmeli
BAGLAM = re.compile(r'ders|program|disiplin|öğretim')

def trlow(s):
    return s.replace('İ','i').replace('I','ı').lower()

def temiz(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'(\w)- (\w)', r'\1\2', s)
    return s

def cumle(metin, poz):
    """Verilen konumu içeren cümleyi döndür."""
    bas = max(metin.rfind('.', 0, poz-1), metin.rfind('\n\n', 0, poz))
    son = metin.find('.', poz)
    if bas < 0: bas = max(0, poz-260)
    if son < 0: son = min(len(metin), poz+260)
    return temiz(metin[bas+1:son+1])[:330]

sonuc = defaultdict(lambda: defaultdict(list))   # kod -> hedef ders -> [alıntı]
istat = defaultdict(int)
oge_istat = defaultdict(int)

for stem, ders, tam_pat, kisa_pat in PROGRAMLAR:
    metin = open(os.path.join(DIR, stem + '.txt'), encoding='utf-8').read()
    metin = re.sub(r'(?m)^\s*\d{1,3}\s*$', '', metin)

    # tema blokları: DERS SAATİ çapası (parse_temalar ile aynı mantık)
    saatler = [m.start() for m in re.finditer(r'DERS SAATİ', metin)]
    for i, s in enumerate(saatler):
        son = saatler[i+1] - 200 if i+1 < len(saatler) else min(len(metin), s + 40000)
        blok = metin[s:son]
        if len(blok) > 60000: continue
        if 'Temel Kabuller' not in blok and 'Köprü Kurma' not in blok: continue

        # bloktaki çıktı kodu konumları (tam kod; yoksa kısa kod tam koda çevrilir)
        isaretler = []
        for m in re.finditer(tam_pat, blok):
            isaretler.append((m.start(), m.group(0)))
        onek = tam_pat.split('\\.')[0].replace('\\', '')
        if kisa_pat:
            for m in re.finditer(r'(?m)(?:^|\s)(' + kisa_pat + r')\.?(?=\s|$)', blok):
                isaretler.append((m.start(1), onek + '.' + m.group(1)))
        if not isaretler: continue
        isaretler.sort()

        # plan ögesi etiketlerinin blok içindeki konumları
        OGELER = [('Temel Kabuller', 'Temel Kabuller'), ('Ön Değerlendirme', 'Ön Değerlendirme Süreci'),
                  ('Köprü Kurma', 'Köprü Kurma'), ('Öğrenme-Öğretme\s*Uygulamaları', 'Öğrenme-Öğretme Uygulamaları'),
                  ('Zenginleştirme', 'Farklılaştırma · Zenginleştirme'), ('Destekleme', 'Farklılaştırma · Destekleme'),
                  ('ÖĞRENME\s*KANITLARI', 'Öğrenme Kanıtları'), ('İÇERİK ÇERÇEVESİ', 'İçerik Çerçevesi')]
        oge_poz = []
        for pat, ad in OGELER:
            for mm in re.finditer(pat, blok):
                oge_poz.append((mm.start(), ad))
        oge_poz.sort()
        def oge_bul(p):
            ad = ''
            for q, a in oge_poz:
                if q <= p: ad = a
                else: break
            return ad

        # segmentlere böl
        for j, (poz, kod) in enumerate(isaretler):
            seg_son = isaretler[j+1][0] if j+1 < len(isaretler) else len(blok)
            seg = blok[poz:seg_son]
            if len(seg) < 60: continue          # sadece kod listesi satırı
            if len(seg) > 6000: seg = seg[:6000]
            dseg = trlow(seg)
            for hedef, kalip in DERS_KALIP:
                if hedef == ders: continue      # kendine atıf sayılmaz
                for m in re.finditer(kalip, dseg):
                    pencere = dseg[max(0,m.start()-90):m.end()+90]
                    if not BAGLAM.search(pencere): continue
                    alinti = cumle(seg, m.start())
                    if len(alinti) < 25: continue
                    # tema düzeyi meta satırları çıktıya özgü kanıt değildir
                    if re.search(r'DİSİPLİNLER ARASI|BECERİLER ARASI|PROGRAMLAR ARASI|ALAN\s*BECERİLERİ|KAVRAMSAL\s*BECERİLER', alinti):
                        continue
                    # büyük harf oranı yüksekse etiket bloğudur
                    harf = [c for c in alinti if c.isalpha()]
                    if harf and sum(c.isupper() for c in harf)/len(harf) > 0.45: continue
                    oge = oge_bul(poz + m.start())
                    kayit = {'a': alinti, 'o': oge}
                    if all(x['a'] != alinti for x in sonuc[kod][hedef]):
                        sonuc[kod][hedef].append(kayit)
                        istat[ders+' → '+hedef] += 1
                        oge_istat[oge or '(belirsiz)'] += 1
                    break                        # ders başına tek kanıt yeterli

# çıktılar.json ile eşleştir, yalnız gerçek çıktı kodlarını tut
ck = {c['code']: c for c in json.load(open(os.path.join(VERI, 'ogrenme-ciktilari.json'), encoding='utf-8'))}
out = {}
for kod, hedefler in sonuc.items():
    if kod not in ck: continue
    c = ck[kod]
    out[kod] = {'ders': c['ders'], 'sinif': c['sinif'], 'temaNo': c['temaNo'], 'tema': c['tema'],
                'statement': c['statement'],
                'kopru': {h: v[:2] for h, v in hedefler.items()}}

json.dump(out, open(os.path.join(VERI, 'cikti-duzeyi-kopruler.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('köprü kuran çıktı:', len(out), '/ toplam çıktı:', len(ck))
print('toplam çıktı-ders bağı:', sum(len(v['kopru']) for v in out.values()))
print('--- köprünün doğduğu plan ögesi ---')
for k, n in sorted(oge_istat.items(), key=lambda x: -x[1]):
    print(f'{n:4}  {k}')
print('--- en sık ders çiftleri ---')
for k, n in sorted(istat.items(), key=lambda x: -x[1])[:12]:
    print(f'{n:4}  {k}')


# ---------------- Harita veri seti (araclar/disiplinler-haritasi.html için) ----------------
ESLE = {
 'Türkçe':'Türkçe','Matematik':'Matematik','Fen Bilimleri':'Fen Bilimleri','Sosyal Bilgiler':'Sosyal Bilgiler',
 'Din Kültürü ve Ahlak Bilgisi':'Din Kültürü ve Ahlak Bilgisi','Din Kültürü':'Din Kültürü ve Ahlak Bilgisi',
 'T.C. İnkılap Tarihi ve Atatürkçülük':'T.C. İnkılap Tarihi ve Atatürkçülük','İnkılap Tarihi':'T.C. İnkılap Tarihi ve Atatürkçülük',
 'Bilişim Teknolojileri ve Yazılım':'Bilişim Teknolojileri ve Yazılım','Bilişim Teknolojileri':'Bilişim Teknolojileri ve Yazılım',
 'Teknoloji ve Tasarım':'Teknoloji ve Tasarım','Beden Eğitimi ve Spor':'Beden Eğitimi ve Spor',
 'Beden Eğitimi ve Oyun':'Beden Eğitimi ve Spor','Görsel Sanatlar':'Görsel Sanatlar','Müzik':'Müzik',
 'İngilizce':'İngilizce','Yabancı Dil':'İngilizce','Hayat Bilgisi':'Hayat Bilgisi',
 'İnsan Hakları':'İnsan Hakları ve Vatandaşlık','Trafik Güvenliği':'Trafik Güvenliği',
}
KOD_RE2 = re.compile(r'\b(KB\d[\d.]*|SDB\d[\d.]*|OB\d+|E\d\.\d+|D\d+(?:\.\d+)?)\b')

def _hedefler(txt):
    txt = re.split(r'BECERİLER ARASI|KB\d|SDB\d|PROGRAMLAR ARASI', txt)[0]
    bulunan = []
    for ad, kanon in ESLE.items():
        if ad in txt and kanon not in bulunan:
            bulunan.append(kanon)
    return bulunan

temalar = json.load(open(os.path.join(VERI, 'temalar.json'), encoding='utf-8'))
beceriler = json.load(open(os.path.join(VERI, 'beceriler.json'), encoding='utf-8'))
ciktilar = json.load(open(os.path.join(VERI, 'ogrenme-ciktilari.json'), encoding='utf-8'))

adet = {}
for c in ciktilar:
    k = (c['ders'], c['sinif'], c['temaNo'])
    adet[k] = adet.get(k, 0) + 1

h_temalar = []
for t in temalar:
    hs = [h for h in _hedefler(t.get('disiplinler', '')) if h != t['ders']] if t.get('disiplinler') else []
    kodset = sorted(set(KOD_RE2.findall(' '.join(
        str(t.get(k, '')) for k in ['egilimler', 'sdb', 'degerler', 'okuryazarlik', 'kavramsal']))))
    h_temalar.append({'ders': t['ders'], 'sinif': t['sinif'], 'temaNo': t['temaNo'], 'tema': t['tema'],
                      'hedefler': hs, 'kod': kodset,
                      'cikti': adet.get((t['ders'], t['sinif'], t['temaNo']), 0)})

ck_idx = {}
for kod, v in out.items():
    k = f"{v['ders']}|{v['sinif']}|{v['temaNo']}"
    ck_idx.setdefault(k, []).append({'c': kod, 's': v['statement'][:220], 'k': v['kopru']})
for k in ck_idx:
    ck_idx[k].sort(key=lambda x: x['c'])

harita = {
    'temalar': h_temalar,
    'kodlar': {e['code']: {'n': e['name'], 'd': e['def'][:150] + ('…' if len(e['def']) > 150 else '')}
               for e in beceriler},
    'ciktiKopru': ck_idx,
}
json.dump(harita, open(os.path.join(VERI, 'harita.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('harita.json →', len(h_temalar), 'tema,',
      sum(1 for x in h_temalar if x['hedefler']), 'bağlantılı,', len(ck_idx), 'çıktı kanıtlı tema')
