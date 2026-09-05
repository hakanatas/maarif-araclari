#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TYMM beceri çerçevesi sayfalarını (HTML) yapılandırılmış JSON'a çevirir."""
import re, json, html as htmlmod, os

import os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'kaynak')
VERI = os.path.join(KOK, 'veri')
os.makedirs(VERI, exist_ok=True)
BASE = os.path.join(KAYNAK, 'beceri_html')
METIN = os.path.join(KAYNAK, 'metin')

NAV_WORDS = {'Süreç bileşenleri', 'Süreç Bileşenleri', 'Göstergeler', 'Daha fazla oku', 'İncele',
             'Türkiye Yüzyılı Maarif Modeli', 'T.C. Milli Eğitim Bakanlığı', '&nbsp;'}

def segs(fn):
    raw = open(os.path.join(BASE, fn), encoding='utf-8').read()
    body = re.sub(r'<(script|style)[\s\S]*?</\1>', '', raw)
    text = re.sub(r'<[^>]+>', '|', body)
    text = re.sub(r'\|+', '|', text)
    out = []
    for s in text.split('|'):
        s = htmlmod.unescape(s).replace('\xa0', ' ').strip()
        s = re.sub(r'\s+', ' ', s)
        if s and s != '-->':
            out.append(s)
    # footer'ı kes
    for i, s in enumerate(out):
        if s == 'T.C. Milli Eğitim Bakanlığı' and i > 40:
            return out[:i-1]  # önceki 'Türkiye Yüzyılı Maarif Modeli' de footer
    return out

def split_code_name(s, code_re):
    m = re.match(code_re, s)
    if not m:
        return None, None
    code = m.group(1).rstrip('.')
    name = s[m.end():].strip(' .-–')
    return code, name

entries = []   # her kod bir giriş
def add(code, name, fw, group, groupName, definition=None, sb=None, refs=None):
    entries.append({'code': code, 'name': name, 'fw': fw, 'group': group,
                    'groupName': groupName, 'def': definition or '',
                    'sb': sb or [], 'refs': refs or []})

def is_def(s):
    return s not in NAV_WORDS and not re.match(r'^(KB|SDB|OB|E|D|MAB|TAB|FBAB|SBAB|SAB|BEOSAB|BTYAB|TSRMAB|DAB|YDAB)\d', s)

# ---------- KB / E / SDB / D / OB (hiyerarşik sayfalar) ----------
def parse_hier(fn, fw, grp_re, item_re, sb_re=None, g_re=None, sub_as_sb=None):
    ss = segs(fn)
    group, groupName, groupDef = None, None, None
    cur = None
    started = False
    for s in ss:
        # SB ve gösterge kontrolleri, öge kontrolünden ÖNCE gelmeli
        # (KB2.1.SB1... aksi hâlde öge sanılıyor)
        if g_re and re.match(g_re, s) and cur is not None and cur['sb']:
            code = s.split(' ')[0].rstrip('.')
            text = s[len(s.split(' ')[0]):].strip()
            cur['sb'][-1]['g'].append(text)
            continue
        if sb_re and re.match(sb_re, s) and cur is not None:
            code = s.split(' ')[0].rstrip('.')
            text = s[len(s.split(' ')[0]):].strip(' .')
            cur['sb'].append({'code': code, 'text': text, 'g': []})
            continue
        if sub_as_sb and re.match(sub_as_sb, s) and cur is not None:
            parts = s.split(' ', 1)
            cur['sb'].append({'code': parts[0].rstrip('.'), 'text': parts[1] if len(parts) > 1 else '', 'g': []})
            continue
        gc, gn = split_code_name(s, grp_re)
        ic, iname = split_code_name(s, item_re) if item_re else (None, None)
        if gc and not ic:
            started = True
            if cur: entries.append(cur); cur = None
            group, groupName = gc, gn
            groupDef = 'PENDING'
            continue
        if not started:
            continue
        if ic:
            if cur: entries.append(cur)
            groupDef = None
            cur = {'code': ic, 'name': iname, 'fw': fw, 'group': group,
                   'groupName': groupName, 'def': '', 'sb': [], 'refs': []}
            continue
        if s in NAV_WORDS:
            continue
        # düz metin: grup ya da öge tanımı
        if cur is not None and not cur['def'] and not cur['sb']:
            cur['def'] = s
        elif groupDef == 'PENDING':
            add(group, groupName, fw, None, None, s)   # grup girişini tanımıyla ekle
            groupDef = None
    if cur: entries.append(cur)
    if groupDef == 'PENDING' and group:
        add(group, groupName, fw, None, None, '')

parse_hier('kavramsal-beceriler.html', 'KB',
           grp_re=r'^(KB\d)\.(?=[A-ZÇĞİÖŞÜ])',
           item_re=r'^(KB\d\.\d+(?:\.\d+)?)\.(?=\s?[A-ZÇĞİÖŞÜ])',
           sb_re=r'^KB\d\.\d+(?:\.\d+)?\.?\s?SB\d')

parse_hier('egilimler.html', 'E',
           grp_re=r'^(E\d)\.(?=[A-ZÇĞİÖŞÜ])',
           item_re=r'^(E\d\.\d+)\.(?=\s?[A-ZÇĞİÖŞÜ])')

parse_hier('sosyal-duygusal-ogrenme-becerileri.html', 'SDB',
           grp_re=r'^(SDB\d)\.(?=[A-ZÇĞİÖŞÜ])',
           item_re=r'^(SDB\d\.\d+)\.?\s?(?=[A-ZÇĞİÖŞÜ(])',
           sb_re=r'^SDB\d\.\d+\.?\s?SB\d+(?!\.G)',
           g_re=r'^SDB\d\.\d+\.?\s?SB\d+\.G\d')

parse_hier('erdem-deger-eylem-cercevesi.html', 'D',
           grp_re=r'^(D\d+)\.(?=[A-ZÇĞİÖŞÜ])',
           item_re=r'^(D\d+\.\d+)\.(?=\s?[A-ZÇĞİÖŞÜa-zçğıöşü])',
           sub_as_sb=r'^D\d+\.\d+\.\d+\.')

parse_hier('okuryazarlik-becerileri.html', 'OB',
           grp_re=r'^(OB\d+)\.(?=\s?[A-ZÇĞİÖŞÜ])',
           item_re=r'^(OB\d+\.\d+)\.(?=\s?[A-ZÇĞİÖŞÜ])',
           sb_re=r'^OB\d+\.\d+\.?\s?SB\d')

# ---------- Alan becerileri sayfaları ----------
ALAN = [
    ('ab-turkce.html', 'TAB', 'Türkçe'),
    ('ab-matematik.html', 'MAB', 'Matematik'),
    ('ab-fen-bilimleri.html', 'FBAB', 'Fen Bilimleri'),
    ('ab-sosyal-bilimler.html', 'SBAB', 'Sosyal Bilimler'),
    ('ab-sanat.html', 'SAB', 'Sanat'),
    ('ab-beden-egitimi-oyun-ve-spor.html', 'BEOSAB', 'Beden Eğitimi, Oyun ve Spor'),
    ('ab-bilisim-teknolojileri-ve-yazilim.html', 'BTYAB', 'Bilişim Tek. ve Yazılım'),
    ('ab-tasarim.html', 'TSRMAB', 'Tasarım'),
    ('ab-din-egitimi-ve-ogretimi.html', 'DAB', 'Din Eğitimi ve Öğretimi'),
]

for fn, fwcode, fwad in ALAN:
    ss = segs(fn)
    grp_re = re.compile(r'^(.{3,80}?)\s*\((' + fwcode + r'\d+)\)$')
    item_re = re.compile(r'^(' + fwcode + r'\d+\.\d+(?:\.\d+)?)\.?\s?(?=[A-ZÇĞİÖŞÜ])')
    sb_re = re.compile(r'^' + fwcode + r'\d+\.\d+(?:\.\d+)?\.?\s?SB\d')
    kbref_re = re.compile(r'^(KB\d\.\d+)\.?\s')
    group, groupName, cur, started = None, None, None, False
    groupPendingDef = False
    for s in ss:
        gm = grp_re.match(s)
        if gm:
            started = True
            if cur: entries.append(cur); cur = None
            group, groupName = gm.group(2), gm.group(1)
            groupPendingDef = True
            continue
        if not started:
            continue
        im = item_re.match(s)
        if im and not sb_re.match(s):
            if cur: entries.append(cur)
            groupPendingDef = False
            name = s[im.end():].strip(' .-–')
            cur = {'code': im.group(1), 'name': name, 'fw': fwcode, 'group': group,
                   'groupName': groupName, 'def': '', 'sb': [], 'refs': []}
            continue
        if sb_re.match(s):
            if cur is not None:
                code = re.match(r'^\S+(?:\s?SB\d+)?', s).group(0)
                m2 = re.match(r'^(' + fwcode + r'[\d.]+\.?\s?SB\d+)\.?\s*(.*)$', s)
                if m2:
                    cur['sb'].append({'code': m2.group(1).replace(' ', ''), 'text': m2.group(2), 'g': []})
            continue
        km = kbref_re.match(s)
        if km:
            # grubun akışındaki kavramsal beceri referansı
            for e in entries:
                pass
            tgt = cur if cur is not None else None
            ref = km.group(1)
            if tgt is not None:
                if ref not in tgt['refs']: tgt['refs'].append(ref)
            else:
                # grup girişi henüz eklenmedi; geçici sakla
                grefs.append(ref) if 'grefs' in dir() else None
            continue
        if re.match(r'^KB\d\.\d+\.?\s?SB\d', s):
            continue  # KB referansının SB'leri — KB çerçevesinde zaten var
        if s in NAV_WORDS:
            continue
        if groupPendingDef:
            add(group, groupName, fwcode, None, None, s)
            groupPendingDef = False
            continue
        if cur is not None and not cur['def'] and not cur['sb']:
            cur['def'] = s
    if cur: entries.append(cur)
    if groupPendingDef and group:
        add(group, groupName, fwcode, None, None, '')

# ---------- Yabancı dil: aynı kod üç pedagojik yaklaşımda tekrarlanıyor → özel ele alış ----------
YD_NOTE = ('Bu beceri için programda üç ayrı pedagojik yaklaşıma göre (bütüncül, '
           'yarı bütüncül-yarı tümevarımsal, tümevarımsal) ayrı süreç bileşeni setleri '
           'tanımlanmıştır; ayrıntı için İngilizce (2-8) Öğretim Programı PDF\'ine bakınız.')
yss = segs('ab-yabanci-dil.html')
yd_grp = re.compile(r'^(?:\d+\.\d+\.|\d+\.)?\s*(.{3,70}?)\s*\((YD[AD]B\d+)\)$')
cur = None
seen_yd = set()
for i, s in enumerate(yss):
    m = yd_grp.match(s)
    if m and m.group(2) not in seen_yd:
        seen_yd.add(m.group(2))
        code, name = m.group(2), m.group(1)
        fw = 'YDAB' if code.startswith('YDAB') else 'YDDB'
        # tanım: sonraki kod-olmayan segment
        d = ''
        for t in yss[i+1:i+3]:
            if not re.match(r'^(YD|KB|\d)', t) and t not in NAV_WORDS and not yd_grp.match(t):
                d = t; break
        add(code, name, fw, None, None, (d + ' ' + YD_NOTE).strip())

# fiziksel beceriler: tek tanıtım metni, kodsuz → tek giriş
fss = segs('fiziksel-beceriler.html')
try:
    i = fss.index('Fiziksel Beceriler', 40)
    fdef = ' '.join(x for x in fss[i+1:i+4] if is_def(x))[:600]
except ValueError:
    fdef = ''
add('FB', 'Fiziksel Beceriler', 'FB', None, None, fdef)

# tekilleştir (aynı kod iki kez eklendiyse ilkini tut)
seen, uniq = set(), []
for e in entries:
    if e['code'] in seen: continue
    seen.add(e['code']); uniq.append(e)

json.dump(uniq, open(os.path.join(VERI, 'beceriler.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
from collections import Counter
print('Toplam giriş:', len(uniq))
print(Counter(e['fw'] for e in uniq))


# ---------------- Kod kullanım sayımı (program metinlerinden) ----------------
DERSLER = {
 'Turkce_5-8_Ogretim_Programi': 'Türkçe',
 'Matematik_5-8_Ogretim_Programi': 'Matematik',
 'Fen_Bilimleri_3-8_Ogretim_Programi': 'Fen Bilimleri',
 'Sosyal_Bilgiler_4-7_Ogretim_Programi': 'Sosyal Bilgiler',
 'Din_Kulturu_ve_Ahlak_Bilgisi_4-8_Ogretim_Programi': 'Din Kültürü',
 'TC_Inkilap_Tarihi_ve_Ataturkculuk_8_Ogretim_Programi': 'İnkılap Tarihi',
 'Bilisim_Teknolojileri_ve_Yazilim_Ogretim_Programi': 'Bilişim Tek.',
 'Teknoloji_ve_Tasarim_7-8_Ogretim_Programi': 'Teknoloji Tasarım',
 'Beden_Egitimi_ve_Spor_Ogretim_Programi': 'Beden Eğitimi',
 'Gorsel_Sanatlar_Ogretim_Programi': 'Görsel Sanatlar',
 'Muzik_Ogretim_Programi': 'Müzik',
 'Secmeli_Gorgu_Kurallari_ve_Nezaket_Ogretim_Programi': 'Görgü Kuralları (S)',
 'Secmeli_Masal_ve_Destanlarimiz_Ogretim_Programi': 'Masal-Destan (S)',
 'Secmeli_Okuma_Becerileri_Ogretim_Programi': 'Okuma Bec. (S)',
 'Secmeli_Yazarlik_ve_Yazma_Becerileri_Ogretim_Programi': 'Yazarlık (S)',
 # --- ilkokul (Eylül 2026 genişlemesi)
 'Ilkokul_Turkce_1-4_Ogretim_Programi': 'Türkçe',
 'Ilkokul_Matematik_1-4_Ogretim_Programi': 'Matematik',
 'Hayat_Bilgisi_Ogretim_Programi': 'Hayat Bilgisi',
 'Insan_Haklari_Vatandaslik_ve_Demokrasi_Ogretim_Programi': 'İnsan Hak. Vat. Dem.',
 'Beden_Egitimi_ve_Oyun_Ogretim_Programi': 'Beden Eğitimi ve Oyun',
 # --- site tarama genişlemesi (Eylül 2026)
 'Trafik_Guvenligi_Ogretim_Programi': 'Trafik Güvenliği',
 'Secmeli_Kurani_Kerim_Ogretim_Programi': "Kur'an-ı Kerim (S)",
 'Secmeli_Peygamberimizin_Hayati_Ogretim_Programi': 'Peygamberimizin Hayatı (S)',
 'Secmeli_Afet_Bilinci_Ogretim_Programi': 'Afet Bilinci (S)',
 'Secmeli_Ahlak_ve_Vatandaslik_Egitimi_Ogretim_Programi': 'Ahlak ve Vat. Eğitimi (S)',
 'Secmeli_Dijital_Sanatlar_Ogretim_Programi': 'Dijital Sanatlar (S)',
 'Secmeli_Dusunme_Egitimi_Ogretim_Programi': 'Düşünme Eğitimi (S)',
 'Secmeli_Geleneksel_Sanatlar_Ogretim_Programi': 'Geleneksel Sanatlar (S)',
 'Secmeli_Matematik_ve_Bilim_Uygulamalari_Ogretim_Programi': 'Mat. ve Bilim Uyg. (S)',
 'Secmeli_Oyun_Drama_Ogretim_Programi': 'Oyun Etk.: Drama (S)',
 'Secmeli_Oyun_Zeka_Oyunlari_Ogretim_Programi': 'Oyun Etk.: Zekâ Oyunları (S)',
 'Secmeli_Oyun_Satranc_Ogretim_Programi': 'Oyun Etk.: Satranç (S)',
 'Secmeli_Oyun_Geleneksel_Oyunlar_Ogretim_Programi': 'Oyun Etk.: Geleneksel (S)',
 'Secmeli_Robotik_Kodlama_Ogretim_Programi': 'Robotik Kodlama (S)',
 'Secmeli_Yapay_Zeka_Uygulamalari_Ogretim_Programi': 'Yapay Zekâ Uyg. (S)',
 'Secmeli_Proje_Tasarimi_ve_Uygulamalari_Ogretim_Programi': 'Proje Tasarımı (S)',
 'Secmeli_Spor_ve_Fiziki_Etkinlikler_Ogretim_Programi': 'Spor ve Fiziki Etk. (S)',
 'Secmeli_Halk_Oyunlari_Ogretim_Programi': 'Halk Oyunları (S)',
 # --- lise (Eylül 2026)
 'Lise_Beden_Egitimi_ve_Spor_Ogretim_Programi': 'Beden Eğitimi',
 'Lise_Biyoloji_Ogretim_Programi': 'Biyoloji',
 'Lise_Cografya_Ogretim_Programi': 'Coğrafya',
 'Lise_Din_Kulturu_ve_Ahlak_Bilgisi_Ogretim_Programi': 'Din Kültürü',
 'Lise_Felsefe_Ogretim_Programi': 'Felsefe',
 'Lise_Fizik_Ogretim_Programi': 'Fizik',
 'Lise_Gorsel_Sanatlar_Ogretim_Programi': 'Görsel Sanatlar',
 'Lise_Kimya_Ogretim_Programi': 'Kimya',
 'Lise_Kurani_Kerim_Ogretim_Programi': "Kur'an-ı Kerim (S)",
 'Lise_Matematik_Ogretim_Programi': 'Matematik',
 'Lise_Matematik_Uygulamalari_Ogretim_Programi': 'Matematik Uyg. (S)',
 'Lise_Muzik_Ogretim_Programi': 'Müzik',
 'Lise_Peygamberimizin_Hayati_Ogretim_Programi': 'Peygamberimizin Hayatı (S)',
 'Lise_TC_Inkilap_Tarihi_Ogretim_Programi': 'İnkılap Tarihi',
 'Lise_Tarih_Ogretim_Programi': 'Tarih',
 'Lise_Temel_Matematik_Ogretim_Programi': 'Temel Matematik',
 'Lise_Turk_Dili_ve_Edebiyati_Ogretim_Programi': 'Türk Dili ve Edebiyatı',
}
# İngilizce programları kodları İngilizce adlarıyla kullanır
ENG_MAP = {'KB': 'CS', 'SDB': 'SELS', 'D': 'V', 'E': 'D'}
ENG_DOSYA = ['Ingilizce_2-8_Ogretim_Programi', 'Coklu_Yabanci_Dil_Modeli_Ingilizce']

def _oku(stem):
    p = os.path.join(METIN, stem + '.txt')
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

# Metin hacmi liseyle birlikte ~15 MB'a çıktı; kod başına ayrı tarama
# (444 × metin) saatler sürer. Tek geçişte bütün kod görünümlerini sayıp
# sözlükten okuyoruz. Dışlama kuralları eski desenle birebir: kodun ardından
# rakam / .rakam / (.)SB / (.)G+rakam geliyorsa sayılmaz.
_TOKEN = re.compile(r'(?<![A-Za-z0-9.])([A-ZÇĞİÖŞÜ]+\d[\d.]*)')
def _sayim_cikar(metin):
    sayim = {}
    for m in _TOKEN.finditer(metin):
        tok = m.group(1).rstrip('.')
        kuyruk = metin[m.end():m.end() + 3]
        if kuyruk[:1].isdigit():
            continue
        if kuyruk[:1] == '.' and kuyruk[1:2].isdigit():
            continue
        if re.match(r'\.?SB', kuyruk) or re.match(r'\.?G\d', kuyruk):
            continue
        sayim[tok] = sayim.get(tok, 0) + 1
    return sayim

def _say(kod, sayim):
    return sayim.get(kod, 0)

# aynı ders adına birden çok belge düşebilir (Türkçe 1-4 + 5-8): metinleri birleştir
metinler = {}
for stem, ad in DERSLER.items():
    metinler[ad] = metinler.get(ad, '') + '\n' + _oku(stem)
metin_sayimlari = {ad: _sayim_cikar(t) for ad, t in metinler.items()}
eng = ''.join(_oku(s) for s in ENG_DOSYA)
eng_sayim = _sayim_cikar(eng)

kullanim = {}
for e in uniq:
    if e['fw'] == 'FB':
        continue
    per = {}
    for ad, sayim in metin_sayimlari.items():
        n = _say(e['code'], sayim)
        if n: per[ad] = n
    if e['fw'] in ENG_MAP and eng_sayim:
        ecode = ENG_MAP[e['fw']] + e['code'][len(e['fw']):]
        n = _say(ecode, eng_sayim)
        if n: per['İngilizce'] = n
    if per:
        kullanim[e['code']] = per

json.dump(kullanim, open(os.path.join(VERI, 'beceri-kullanim.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
print('kullanımı tespit edilen kod:', len(kullanim),
      '| toplam geçiş:', sum(sum(v.values()) for v in kullanim.values()))
