#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18 TYMM ortaokul programından öğrenme çıktılarını ayrıştırır."""
import re, json, os

import os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'kaynak')
VERI = os.path.join(KOK, 'veri')
os.makedirs(VERI, exist_ok=True)
DIR = os.path.join(KAYNAK, 'metin')

# stem -> (ders adı, kod öneki, biçim)
# biçim: 'gtn' = ÖNEK.sınıf.tema.no | 'dtn' = ÖNEK.düzey.tema.no | 'tn' = ÖNEK.tema.no | 'turkce' = T.<alan>.sınıf.no
PROGRAMLAR = [
 ('Turkce_5-8_Ogretim_Programi', 'Türkçe', 'T', 'turkce'),
 ('Matematik_5-8_Ogretim_Programi', 'Matematik', 'MAT', 'gtn'),
 ('Fen_Bilimleri_3-8_Ogretim_Programi', 'Fen Bilimleri', 'FB', 'gttn'),
 ('Sosyal_Bilgiler_4-7_Ogretim_Programi', 'Sosyal Bilgiler', 'SB', 'gtn'),
 ('Din_Kulturu_ve_Ahlak_Bilgisi_4-8_Ogretim_Programi', 'Din Kültürü ve Ahlak Bilgisi', 'DKAB', 'gtn'),
 ('TC_Inkilap_Tarihi_ve_Ataturkculuk_8_Ogretim_Programi', 'T.C. İnkılap Tarihi ve Atatürkçülük', 'İTA', 'gtn'),
 ('Bilisim_Teknolojileri_ve_Yazilim_Ogretim_Programi', 'Bilişim Teknolojileri ve Yazılım', 'BTY', 'gtn'),
 ('Teknoloji_ve_Tasarim_7-8_Ogretim_Programi', 'Teknoloji ve Tasarım', 'TT', 'gtn'),
 ('Beden_Egitimi_ve_Spor_Ogretim_Programi', 'Beden Eğitimi ve Spor', 'BES', 'gtn'),
 ('Gorsel_Sanatlar_Ogretim_Programi', 'Görsel Sanatlar', 'GS', 'gtn'),
 ('Muzik_Ogretim_Programi', 'Müzik', 'MÜZ', 'gtn'),
 ('Secmeli_Gorgu_Kurallari_ve_Nezaket_Ogretim_Programi', 'Görgü Kuralları ve Nezaket (Seçmeli)', 'GKN', 'dtn'),
 ('Secmeli_Masal_ve_Destanlarimiz_Ogretim_Programi', 'Masal ve Destanlarımız (Seçmeli)', 'MD', 'dtn'),
 ('Secmeli_Yazarlik_ve_Yazma_Becerileri_Ogretim_Programi', 'Yazarlık ve Yazma Becerileri (Seçmeli)', 'YYB', 'dtn'),
 ('Secmeli_Okuma_Becerileri_Ogretim_Programi', 'Okuma Becerileri (Seçmeli)', 'OB', 'tn'),
]

TR_ALAN = {'D': 'Dinleme/İzleme', 'O': 'Okuma', 'K': 'Konuşma', 'Y': 'Yazma'}
SB_MARK = re.compile(r'^\s*([a-zçğıöşü])\)\s+')
REF_RE = re.compile(r'\b(KB\d[\d.]*|SDB\d[\d.]*|OB\d[\d.]*|E\d\.\d+|D\d+(?:\.\d+)?|MAB\d?[\d.]*|TAB\d[\d.]*|FBAB\d[\d.]*|SBAB\d[\d.]*|SAB\d[\d.]*|BEOSAB\d[\d.]*|BTYAB\d[\d.]*|TSRMAB\d[\d.]*|DAB\d[\d.]*|YDAB\d[\d.]*|YDDB\d[\d.]*)\b')

def header_gibi(line):
    s = line.strip()
    if not s: return False
    if re.match(r'^\d+$', s): return True            # sayfa numarası
    if 'ÖĞRETİM PROGRAMI' in s.upper() and s == s.upper(): return True
    up = s.upper()
    if s == up and len(s) > 12 and not SB_MARK.match(s):  # tam büyük harfli başlıklar
        return True
    return False

DURDUR = re.compile(r'^\s*(İÇERİK ÇERÇEVESİ|ÖĞRENME KANITLARI|ÖĞRENME-ÖĞRETME|TEMEL KABULLER|Genellemeler|Anahtar Kavramlar|FARKLILAŞTIRMA|BECERİLER ARASI|DİSİPLİNLER ARASI|PROGRAMLAR ARASI|OKUL TEMELLİ|ÖĞRETMEN YANSITMALARI)', re.I)

def tr_baslik(s):
    kucuk = {'I':'ı','İ':'i','Ç':'ç','Ğ':'ğ','Ö':'ö','Ş':'ş','Ü':'ü'}
    out = []
    BAGLAC = {'ve','ile','de','da','mi','mı','mu','mü','için'}
    for w in s.split():
        if not w: continue
        tam = ''.join(kucuk.get(ch, ch.lower()) for ch in w)
        if tam in BAGLAC and out:
            out.append(tam); continue
        ilk = w[0]
        geri = ''.join(kucuk.get(ch, ch.lower()) for ch in w[1:])
        out.append(ilk + geri)
    return ' '.join(out)

def temiz(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace('­', '').replace('\t', ' ')
    s = re.sub(r'(\w)- (\w)', r'\1\2', s)  # satır sonu tire birleşimi
    return s

def parse_program(stem, ders, onek, bicim):
    yol = os.path.join(DIR, stem + '.txt')
    metin = open(yol, encoding='utf-8').read()
    lines = metin.split('\n')

    if bicim == 'turkce':
        code_re = re.compile(r'\b(T\.[DOKY]\.[1-8]\.\d{1,2})\.(?!\d)')
    elif bicim == 'gttn':
        code_re = re.compile(r'\b(' + onek + r'\.\d\.\d{1,2}\.\d{1,2}\.\d{1,2})\.(?!\d)')
    elif bicim == 'tn':
        code_re = re.compile(r'\b(' + onek + r'\.\d{1,2}\.\d{1,2})\.(?!\d)')
    else:
        code_re = re.compile(r'\b(' + onek + r'\.\d\.\d{1,2}\.\d{1,2})\.(?!\d)')

    # tema adları: sınıf bağlamı + "1.TEMA: AD"
    tema_ad = {}
    sinif_ctx = None
    for ln in lines:
        m = re.match(r'^\s*(\d)\.\s*SINIF\b', ln)
        if m: sinif_ctx = m.group(1)
        m = re.match(r'^\s*DÜZEY[ -]*(I{1,3})\b', ln)
        if m: sinif_ctx = str(len(m.group(1)))
        m = re.match(r'^\s*(\d{1,2})\.\s*(?:TEMA|ÜNİTE|ÖĞRENME ALANI):?\s*(.{3,80})$', ln)
        if m:
            ad = temiz(m.group(2))
            ad = re.sub(r'\s*\(\d+\)\s*$', '', ad)
            ad = tr_baslik(ad) if ad == ad.upper() else ad
            if sinif_ctx: tema_ad[(sinif_ctx, m.group(1))] = ad
            k = ('*', m.group(1))
            if k not in tema_ad or len(ad) > len(tema_ad[k]): tema_ad[k] = ad

    adaylar = {}   # code -> en iyi kayıt
    cur = None

    def kapat():
        nonlocal cur
        if not cur: return
        code = cur['code']
        cur['statement'] = temiz(cur['statement'])[:600]
        cur['sb'] = [temiz(x)[:600] for x in cur['sb'] if temiz(x)]
        eski = adaylar.get(code)
        puan = (len(cur['sb']), len(cur['statement']))
        if not eski or puan > (len(eski['sb']), len(eski['statement'])):
            adaylar[code] = cur
        cur = None

    for ln in lines:
        m = code_re.search(ln)
        # kod satırı: satırda koddan önce en fazla kısa bir etiket olmalı (düz yazı içi atıfları ele)
        on_metin = ln[:m.start()].strip() if m else ''
        if m and (m.start() < 40 or 'BİLEŞENLER' in on_metin.upper()) and not re.search(r'(Uygulamaları|Uygulama|Öğretme|bk\.|bkz)\s*$', on_metin):
            kapat()
            rest = ln[m.end():].strip()
            chain = [m.group(1)]
            if bicim == 'turkce' and rest.startswith('/'):
                # "T.O.5.1. / T.O.6.1. / ..." zinciri: tüm kodları al, adı zincirden sonrası yap
                tumkod = re.findall(r'T\.[DOKY]\.[1-8]\.\d{1,2}', ln)
                chain = list(dict.fromkeys(tumkod))
                rest = re.sub(r'^[\s/.]*(T\.[DOKY]\.[1-8]\.\d{1,2}[\s/.]*)*', '', ln[m.end():]).strip()
            cur = {'code': m.group(1), 'chain': chain, 'statement': rest, 'sb': []}
            continue
        if cur is None:
            continue
        if DURDUR.match(ln) or header_gibi(ln):
            kapat(); continue
        if SB_MARK.match(ln):
            cur['sb'].append(SB_MARK.sub('', ln))
        elif ln.strip():
            if cur['sb']:
                cur['sb'][-1] += ' ' + ln.strip()
            else:
                cur['statement'] += ' ' + ln.strip()
        # boş satır: devam (tablo akışında sık)
    kapat()

    # Türkçe: ad ile açıklamayı ayır, zincir kodlarını genişlet
    if bicim == 'turkce':
        genis = {}
        for code, k in adaylar.items():
            st = k['statement']
            ad, acik = st, ''
            # ad "…bilme/…uyarlayabilme" ile biter; ilk 220 karakterdeki son 'bilme' sınırını al
            eslesme = None
            for mm in re.finditer(r'bilme(?:/kendini uyarlayabilme|/kendine uyarlayabilme)?\b', st[:220]):
                eslesme = mm
            if eslesme:
                ad, acik = st[:eslesme.end()].strip(), st[eslesme.end():].strip()
            for c in k.get('chain', [code]):
                yeni = dict(k); yeni['code'] = c; yeni['statement'] = ad; yeni['aciklama'] = acik[:700]
                eski = genis.get(c)
                if not eski or len(yeni.get('aciklama','')) > len(eski.get('aciklama','')):
                    genis[c] = yeni
        adaylar = genis

        # onarım: şüpheli/boş adları, metindeki "KOD. Ad…bilme" satırlarından düzelt
        adlik = {}
        birlesik = re.sub(r'\n(?![A-ZÇĞİÖŞÜT])', ' ', metin)  # ad satırı sarmalarını birleştir
        for mm in re.finditer(r'((?:T\.[DOKY]\.[1-8]\.\d{1,2}\.\s*/?\s*)+)\s*([A-ZÇĞİÖŞÜ][^\n]{5,180}?bilme(?:/kendini uyarlayabilme|/kendine uyarlayabilme)?)(?=[\s.]|$)', birlesik):
            adtxt = temiz(mm.group(2))
            for c in re.findall(r'T\.[DOKY]\.[1-8]\.\d{1,2}', mm.group(1)):
                if c not in adlik or len(adtxt) < len(adlik[c]):
                    adlik[c] = adtxt
        for c, k in adaylar.items():
            st = k['statement']
            if (not st or not re.match(r'^[A-ZÇĞİÖŞÜ“"\']', st) or 'bilme' not in st[:220]) and c in adlik:
                k['statement'] = adlik[c]
                if not k.get('aciklama'): k['aciklama'] = ''

    sonuc = []
    for code, k in adaylar.items():
        p = code.split('.')
        if bicim == 'turkce':
            g, tema, tno = p[2], TR_ALAN.get(p[1], p[1]), p[3]
            temaNo = p[1]
        elif bicim == 'gttn':
            g, temaNo, tno = p[1], p[2], p[4]
            tema = tema_ad.get((g, temaNo)) or tema_ad.get(('*', temaNo)) or f'Tema {temaNo}'
        elif bicim == 'tn':
            g, temaNo, tno = '—', p[1], p[2]
            tema = tema_ad.get(('1', temaNo)) or tema_ad.get(('*', temaNo)) or f'Tema {temaNo}'
        else:
            g, temaNo, tno = p[1], p[2], p[3]
            tema = tema_ad.get((g, temaNo)) or tema_ad.get(('*', temaNo)) or f'Tema {temaNo}'
            if bicim == 'dtn':
                g = f'Düzey {g}'
        tumu = k['statement'] + ' ' + k.get('aciklama', '') + ' ' + ' '.join(k['sb'])
        refs = sorted(set(REF_RE.findall(tumu)))
        kayit = {'code': code, 'ders': ders, 'sinif': g, 'tema': tema, 'temaNo': temaNo,
                 'statement': k['statement'], 'sb': k['sb'], 'refs': refs}
        if k.get('aciklama'): kayit['aciklama'] = k['aciklama']
        sonuc.append(kayit)
    return sonuc

hepsi = []
for stem, ders, onek, bicim in PROGRAMLAR:
    r = parse_program(stem, ders, onek, bicim)
    print(f'{ders:42} {len(r):4} çıktı')
    hepsi += r

# sıralama: ders, sınıf, tema, çıktı no (doğal sıra)
def anahtar(c):
    def num(x):
        try: return int(re.sub(r'\D', '', x) or 0)
        except: return 0
    return (c['ders'], num(c['sinif']), num(c['temaNo']), num(c['code'].split('.')[-1]))
hepsi.sort(key=anahtar)

json.dump(hepsi, open(os.path.join(VERI, 'ogrenme-ciktilari.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('TOPLAM:', len(hepsi))
sbsiz = sum(1 for c in hepsi if not c['sb'])
print('süreç bileşeni bulunamayan:', sbsiz)
