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
 ('Fen_Bilimleri_3-8_Ogretim_Programi', 'Fen Bilimleri', r'FB\.([1-8])\.(\d{1,2})\.\d{1,2}(?:\.\d{1,2})?', 'kod'),
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
 # --- ilkokul (Eylül 2026 genişlemesi)
 ('Ilkokul_Turkce_1-4_Ogretim_Programi', 'Türkçe', r'T\.[DOKY]\.([1-8])\.\d{1,2}', 'sirali'),
 ('Ilkokul_Matematik_1-4_Ogretim_Programi', 'Matematik', r'MAT\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Hayat_Bilgisi_Ogretim_Programi', 'Hayat Bilgisi', r'HB\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Insan_Haklari_Vatandaslik_ve_Demokrasi_Ogretim_Programi',
  'İnsan Hakları, Vatandaşlık ve Demokrasi', r'İHVD\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Beden_Egitimi_ve_Oyun_Ogretim_Programi', 'Beden Eğitimi ve Oyun', r'BEO\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 # --- site tarama genişlemesi (Eylül 2026)
 ('Trafik_Guvenligi_Ogretim_Programi', 'Trafik Güvenliği', r'TG\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Secmeli_Kurani_Kerim_Ogretim_Programi', "Kur'an-ı Kerim (Seçmeli)", r'KK\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Secmeli_Peygamberimizin_Hayati_Ogretim_Programi', 'Peygamberimizin Hayatı (Seçmeli)', r'PH\.([1-8])\.(\d{1,2})\.\d{1,2}', 'kod'),
 ('Secmeli_Afet_Bilinci_Ogretim_Programi', 'Afet Bilinci (Seçmeli)', r'AB\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Ahlak_ve_Vatandaslik_Egitimi_Ogretim_Programi', 'Ahlak ve Vatandaşlık Eğitimi (Seçmeli)', r'AVE\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Dijital_Sanatlar_Ogretim_Programi', 'Dijital Sanatlar (Seçmeli)', r'DS\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Dusunme_Egitimi_Ogretim_Programi', 'Düşünme Eğitimi (Seçmeli)', r'DE\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Geleneksel_Sanatlar_Ogretim_Programi', 'Geleneksel Sanatlar (Seçmeli)', r'GS\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Matematik_ve_Bilim_Uygulamalari_Ogretim_Programi', 'Matematik ve Bilim Uygulamaları (Seçmeli)', r'MU\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Oyun_Drama_Ogretim_Programi', 'Oyun ve Oyun Etkinlikleri: Drama (Seçmeli)', r'OOED\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Oyun_Zeka_Oyunlari_Ogretim_Programi', 'Oyun ve Oyun Etkinlikleri: Zekâ Oyunları (Seçmeli)', r'OOEZO\.([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Robotik_Kodlama_Ogretim_Programi', 'Robotik Kodlama (Seçmeli)', r'RK\.?([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Yapay_Zeka_Uygulamalari_Ogretim_Programi', 'Yapay Zekâ Uygulamaları (Seçmeli)', r'YZU\.?([1-3])\.(\d{1,2})\.\d{1,2}', 'kod_duzey'),
 ('Secmeli_Oyun_Satranc_Ogretim_Programi', 'Oyun ve Oyun Etkinlikleri: Satranç (Seçmeli)', r'OOEST\.(\d{1,2})\.\d{1,2}', 'tek'),
 ('Secmeli_Oyun_Geleneksel_Oyunlar_Ogretim_Programi', 'Oyun ve Oyun Etkinlikleri: Geleneksel Oyunlar (Seçmeli)', r'OOEGO\.(\d{1,2})\.\d{1,2}', 'tek'),
 ('Secmeli_Proje_Tasarimi_ve_Uygulamalari_Ogretim_Programi', 'Proje Tasarımı ve Uygulamaları (Seçmeli)', r'PTU\.(\d{1,2})\.\d{1,2}', 'tek'),
 ('Secmeli_Spor_ve_Fiziki_Etkinlikler_Ogretim_Programi', 'Spor ve Fiziki Etkinlikler (Seçmeli)', r'SFE\.(\d{1,2})\.\d{1,2}', 'tek'),
 ('Secmeli_Halk_Oyunlari_Ogretim_Programi', 'Halk Oyunları (Seçmeli)', r'HO\.(\d{1,2})\.\d{1,2}', 'tek'),
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

def nokta_sozlugu(metin):
    """PDF'te büyük harfli başlıklarda İ bazen noktasız I'ya düşer (font eşlemesi).
    Aynı metnin gövdesinde doğru yazım bulunduğundan, noktasız izdüşümden noktalı
    biçime bir sözlük kurup başlıkları onarırız. Sabit liste değil, veriye dayalı."""
    soz = {}
    for w in re.findall(r'[A-Za-zÇĞİÖŞÜçğıöşü]{3,}', metin):
        # Türkçe kurallarına göre büyüt: i -> İ, ı -> I
        buyuk = w.replace('i', 'İ').replace('ı', 'I').upper()
        if 'İ' not in buyuk:
            continue
        soz.setdefault(buyuk.replace('İ', 'I'), set()).add(buyuk)
    return soz


def basligi_onar(baslik, soz):
    out = []
    for w in baslik.split():
        if 'I' in w and 'İ' not in w:
            aday = soz.get(w)
            if aday and len(aday) == 1:      # yalnız tek adaylı, kesin durumlar
                w = next(iter(aday))
        out.append(w)
    return ' '.join(out)


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
    nokta_soz = nokta_sozlugu(metin)
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
        # 2026 seçmelilerinde döngü kısaltılmış: Temel Kabuller / Köprü Kurma yok,
        # ama ÖĞRENME ÇIKTILARI VE SÜREÇ BİLEŞENLERİ bloğu var. Süre tabloları
        # "Öğrenme Çıktıları Sayısı" yazar, SÜREÇ BİLEŞENLERİ demez.
        # Satranç/Zekâ Oyunları PDF'lerinde başlıklar sütunlara bölündüğünden
        # "SÜREÇ BİLEŞENLERİ" ifadesi bile bütünleşmiyor; İçerik Çerçevesi ve
        # Öğrenme Kanıtları başlıkları da blok kanıtı sayılır.
        if not any(x in blok for x in ('Temel Kabuller', 'Köprü Kurma', 'SÜREÇ BİLEŞENLERİ',
                                       'İÇERİK ÇERÇEVESİ', 'Öğrenme Kanıtları', 'ÖĞRENME KANITLARI')):
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
        if tema == tema.upper():
            tema = basligi_onar(tema, nokta_soz)

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

        # yalnız yakalayan grupları çevir; desendeki (?: zaten yakalamıyor
        tam_kod_re = re.compile(re.sub(r'\((?!\?)', '(?:', kod_pat))
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
