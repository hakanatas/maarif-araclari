#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Program metinlerinden tema bloklarını (8 ögeli öğretim döngüsü) ayrıştırır."""
import re, json, os

import os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'kaynak')
VERI = os.path.join(KOK, 'veri')
os.makedirs(VERI, exist_ok=True)
DIR = os.path.join(KAYNAK, 'metin')

PROGRAMLAR = [
 ('Turkce_5-8_Ogretim_Programi', 'Türkçe', r'T\.[DOKY]\.([1-8])\.\d{1,2}', 'sirali'),
 ('Matematik_5-8_Ogretim_Programi', 'Matematik', r'MAT\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Fen_Bilimleri_3-8_Ogretim_Programi', 'Fen Bilimleri', r'FB\.([1-8])\.(\d{1,2})\.\d{1,2}\.\d{1,2}', 'kod'),
 ('Sosyal_Bilgiler_4-7_Ogretim_Programi', 'Sosyal Bilgiler', r'SB\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Din_Kulturu_ve_Ahlak_Bilgisi_4-8_Ogretim_Programi', 'Din Kültürü ve Ahlak Bilgisi', r'DKAB\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('TC_Inkilap_Tarihi_ve_Ataturkculuk_8_Ogretim_Programi', 'T.C. İnkılap Tarihi ve Atatürkçülük', r'İTA\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Bilisim_Teknolojileri_ve_Yazilim_Ogretim_Programi', 'Bilişim Teknolojileri ve Yazılım', r'BTY\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Teknoloji_ve_Tasarim_7-8_Ogretim_Programi', 'Teknoloji ve Tasarım', r'TT\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Beden_Egitimi_ve_Spor_Ogretim_Programi', 'Beden Eğitimi ve Spor', r'BES\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Gorsel_Sanatlar_Ogretim_Programi', 'Görsel Sanatlar', r'GS\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Muzik_Ogretim_Programi', 'Müzik', r'MÜZ\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Secmeli_Gorgu_Kurallari_ve_Nezaket_Ogretim_Programi', 'Görgü Kuralları ve Nezaket (Seçmeli)', r'GKN\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Masal_ve_Destanlarimiz_Ogretim_Programi', 'Masal ve Destanlarımız (Seçmeli)', r'MD\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Yazarlik_ve_Yazma_Becerileri_Ogretim_Programi', 'Yazarlık ve Yazma Becerileri (Seçmeli)', r'YYB\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Okuma_Becerileri_Ogretim_Programi', 'Okuma Becerileri (Seçmeli)', r'OB\.(\d{1,2})\.\d{1,2}', 'tek'),
]

ETIKETLER = [
 ('saat', r'DERS SAATİ'),
 ('alan', r'ALAN\s*BECERİLERİ'),
 ('kavramsal', r'KAVRAMSAL\s*BECERİLER'),
 ('egilimler', r'EĞİLİMLER'),
 ('parabirlesen', r'PROGRAMLAR ARASI\s*BİLEŞENLER'),
 ('sdb', r'Sosyal-Duygusal\s*Öğrenme Becerileri'),
 ('degerler', r'Değerler\b'),
 ('okuryazarlik', r'Okuryazarlık Becerileri'),
 ('disiplinler', r'DİSİPLİNLER ARASI\s*İLİŞKİLER'),
 ('beceriler', r'BECERİLER ARASI\s*İLİŞKİLER'),
 ('ciktilar', r'ÖĞRENME ÇIKTILARI\s*(?:VE SÜREÇ BİLEŞENLERİ)?'),
 ('icerik', r'İÇERİK ÇERÇEVESİ'),
 ('kanitlar', r'ÖĞRENME\s*KANITLARI\s*(?:\(Ö?ö?lçme ve\s*Değerlendirme\)|\(ÖLÇME VE\s*DEĞERLENDİRME\))?'),
 ('yasantilar', r'ÖĞRENME-ÖĞRETME\s*YAŞANTILARI'),
 ('temelKabuller', r'Temel Kabuller'),
 ('onDegerlendirme', r'Ön Değerlendirme\s*(?:Süreci)?'),
 ('kopruKurma', r'Köprü Kurma'),
 ('uygulamalar', r'Öğrenme-Öğretme\s*Uygulamaları'),
 ('farklilastirma', r'FARKLILAŞTIRMA'),
 ('zenginlestirme', r'Zenginleştirme'),
 ('destekleme', r'Destekleme'),
 ('okulTemelli', r'OKUL TEMELLİ PLANLAMA'),
 ('yansitmalar', r'ÖĞRETMEN\s*YANSITMALARI'),
]
ET_RE = re.compile('|'.join(f'(?P<{k}>{p})' for k, p in ETIKETLER))
SINIR = ['yansitmalar', 'okulTemelli']  # blok sonu işaretleri

def temiz(s):
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'(\w)- (\w)', r'\1\2', s)

def sayfa_temizle(metin, ders):
    # sayfa başlıkları ve numaraları
    metin = re.sub(r'(?m)^\s*\d{1,3}\s*$', '', metin)
    metin = re.sub(r'(?mi)^.{0,20}(ORTAOKUL )?[A-ZÇĞİÖŞÜ .,\-]*DERS[İI] ÖĞRET[İI]M PROGRAMI\s*$', '', metin)
    return metin

LIMIT = {'uygulamalar': 5000, 'kanitlar': 1500, 'icerik': 1800}
VARSAYILAN_LIMIT = 1600

for_app = []
for stem, ders, kod_pat, mod in PROGRAMLAR:
    metin = open(os.path.join(DIR, stem + '.txt'), encoding='utf-8').read()
    metin = sayfa_temizle(metin, ders)
    kod_re = re.compile(kod_pat)

    # blok sınırları: DERS SAATİ konumları
    saatler = [m.start() for m in re.finditer(r'DERS SAATİ', metin)]
    bloklar = []
    for i, s in enumerate(saatler):
        bas = max(0, s - 2600)            # tema başlığı ve adı geriye doğru
        son = saatler[i+1] - 200 if i+1 < len(saatler) else min(len(metin), s + 40000)
        # blok sonunu bir sonraki bloğun başlangıcından önce kes
        bloklar.append((bas, s, son))

    sirali_sayac = {}
    for bas, saat_poz, son in bloklar:
        blok = metin[saat_poz:son]
        onsoz = metin[bas:saat_poz]

        # gerçek tema bloğu mu? (süre tabloları da DERS SAATİ içerir; dev bloklar örnek-yapı sayfalarıdır)
        if 'Temel Kabuller' not in blok and 'Köprü Kurma' not in blok:
            continue
        if len(blok) > 60000:
            continue
        # anahtar: blokta EN SIK geçen (sınıf, tema) çifti — ilk kod yanıltabilir
        from collections import Counter as _C
        eslesmeler = kod_re.findall(blok[:15000])
        if not eslesmeler: continue
        if mod == 'kod' or mod == 'kod_duzey':
            enSik = _C(eslesmeler).most_common(1)[0][0]
            sinif, temaNo = enSik[0], enSik[1]
            if mod == 'kod_duzey': sinif = 'Düzey ' + sinif
        elif mod == 'tek':
            enSik = _C(eslesmeler).most_common(1)[0][0]
            sinif, temaNo = '—', enSik
        else:  # sirali (Türkçe)
            enSik = _C(eslesmeler).most_common(1)[0][0]
            sinif = enSik
            sirali_sayac[sinif] = sirali_sayac.get(sinif, 0) + 1
            temaNo = str(sirali_sayac[sinif])

        # tema adı: önsözdeki son başlık
        tema = f'Tema {temaNo}'
        for hm in re.finditer(r'(\d{1,2})\.\s*(?:TEMA|ÜNİTE|ÖĞRENME ALANI):?\s*([^\n]{3,90})', onsoz):
            aday = temiz(hm.group(2))
            aday = re.sub(r'\s*\(\d+\)\s*$', '', aday)
            if aday: tema = aday
        # Türkçe: başlık "N. TEMA" tek satır, ad sonraki satırda olabilir
        if tema.startswith('Tema ') :
            hm = None
            for hm in re.finditer(r'(?:TEMA|ÜNİTE)\s*:?\s*\n+\s*([A-ZÇĞİÖŞÜ][^\n]{3,80})', onsoz): pass
            if hm: tema = temiz(hm.group(1))

        # bölümleri kes
        parcalar = {}
        konumlar = [(m.lastgroup, m.start(), m.end()) for m in ET_RE.finditer(blok)]
        for j, (ad, s0, s1) in enumerate(konumlar):
            s_next = konumlar[j+1][1] if j+1 < len(konumlar) else len(blok)
            icerik = temiz(blok[s1:s_next])
            lim = LIMIT.get(ad, VARSAYILAN_LIMIT)
            if len(icerik) > lim: icerik = icerik[:lim].rsplit(' ', 1)[0] + ' …'
            if ad in parcalar and len(parcalar[ad]) >= len(icerik): continue
            parcalar[ad] = icerik
            if ad in SINIR and j > 3: break

        saat = ''
        sm = re.match(r'\s*(\d{1,3})', parcalar.get('saat',''))
        if sm: saat = sm.group(1)

        tam_kod_re = re.compile(kod_pat.replace('(', '(?:'))
        blok_kodlar = sorted(set(m2.group(0) for m2 in tam_kod_re.finditer(blok)))
        kayit = {'ders': ders, 'sinif': sinif, 'temaNo': temaNo, 'tema': tema, 'saat': saat, 'kodlar': blok_kodlar}
        for k in ['alan','kavramsal','egilimler','sdb','degerler','okuryazarlik','disiplinler','beceriler',
                  'icerik','kanitlar','temelKabuller','onDegerlendirme','kopruKurma','uygulamalar',
                  'zenginlestirme','destekleme']:
            v = parcalar.get(k, '')
            # bölüm başlığı artıkları
            v = re.sub(r'^(Süreci|VE SÜREÇ BİLEŞENLERİ|\(Ölçme ve Değerlendirme\)|\(ÖLÇME VE DEĞERLENDİRME\))\s*', '', v)
            if v: kayit[k] = v
        # aynı (ders,sınıf,temaNo) için alan bazında birleştir (en dolu değer kazanır)
        mevcut = next((x for x in for_app if x['ders']==ders and x['sinif']==sinif and x['temaNo']==temaNo), None)
        if mevcut:
            for kk, vv in kayit.items():
                if kk in ('ders','sinif','temaNo'): continue
                if kk == 'kodlar':
                    mevcut['kodlar'] = sorted(set(mevcut.get('kodlar', [])) | set(vv)); continue
                if kk == 'tema' and mevcut.get('tema','').startswith('Tema ') and not str(vv).startswith('Tema '):
                    mevcut['tema'] = vv; continue
                if len(str(vv)) > len(str(mevcut.get(kk, ''))):
                    mevcut[kk] = vv
        else:
            for_app.append(kayit)

from collections import Counter
print(Counter(k['ders'] for k in for_app))
tam = sum(1 for k in for_app if all(x in k for x in ['temelKabuller','kopruKurma','zenginlestirme','destekleme']))
print('TOPLAM tema:', len(for_app), '| 4 ana öge tam olan:', tam)
json.dump(for_app, open(os.path.join(VERI, 'temalar.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
