#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Disiplinler arası köprüleri program metinlerinden çıkarır.

Bir köprü, ancak metinde başka bir dersin adı anıldığında sayılır ve kanıt olarak
o cümle saklanır. Köprünün NEREYE ait olduğu, cümlenin bulunduğu bölgeye bakılarak
belirlenir:

  * Cümle, bir öğrenme çıktısının kendi bölgesindeyse (bölüm başlığından SONRA gelen
    bir çıktı kodunun ardında) -> o çıktıya bağlanır.
  * Cümle, temanın tümüne ait bir bölümdeyse (Köprü Kurma, Ön Değerlendirme,
    Temel Kabuller, Farklılaştırma vb.) -> hiçbir çıktıya bağlanmaz, TEMA düzeyinde
    kaydedilir. Bu ayrım önemlidir: bu bölümler çıktı listesinden sonra geldiği için
    naif bir bölütleme onları son çıktıya yapıştırır ve olmayan bir bağ uydurur.
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

DERS_KALIP = [
 ('Türkçe', r'türkçe'), ('Matematik', r'matematik'), ('Fen Bilimleri', r'fen bilimleri'),
 ('Sosyal Bilgiler', r'sosyal bilgiler'), ('Din Kültürü ve Ahlak Bilgisi', r'din kültürü'),
 ('T.C. İnkılap Tarihi ve Atatürkçülük', r'i̇nkılap tarihi|inkılap tarihi'),
 ('Bilişim Teknolojileri ve Yazılım', r'bilişim teknolojileri'),
 ('Teknoloji ve Tasarım', r'teknoloji ve tasarım'), ('Beden Eğitimi ve Spor', r'beden eğitimi'),
 ('Görsel Sanatlar', r'görsel sanatlar'), ('Müzik', r'müzik'), ('Hayat Bilgisi', r'hayat bilgisi'),
 ('İngilizce', r'i̇ngilizce|ingilizce|yabancı dil'), ('Trafik Güvenliği', r'trafik güvenliği'),
 ('İnsan Hakları ve Vatandaşlık', r'vatandaşlık ve demokrasi'),
]
BAGLAM = re.compile(r'ders|program|disiplin|öğretim')

# tema bloğundaki bölüm başlıkları (sıra önemli değil, konumları kullanılır)
BOLUMLER = [
 (r'İÇERİK ÇERÇEVESİ', 'İçerik Çerçevesi'),
 (r'ÖĞRENME\s*KANITLARI', 'Öğrenme Kanıtları'),
 (r'Temel Kabuller', 'Temel Kabuller'),
 (r'Ön Değerlendirme', 'Ön Değerlendirme Süreci'),
 (r'Köprü Kurma', 'Köprü Kurma'),
 (r'Öğrenme-Öğretme\s*Uygulamaları', 'Öğrenme-Öğretme Uygulamaları'),
 (r'Zenginleştirme', 'Farklılaştırma · Zenginleştirme'),
 (r'Destekleme', 'Farklılaştırma · Destekleme'),
 (r'ÖĞRETMEN\s*YANSITMALARI', 'Öğretmen Yansıtmaları'),
]
BOLUM_RE = re.compile('|'.join(f'(?P<b{i}>{p})' for i, (p, _) in enumerate(BOLUMLER)))
BOLUM_AD = {f'b{i}': ad for i, (_, ad) in enumerate(BOLUMLER)}

def trlow(s): return s.replace('İ', 'i').replace('I', 'ı').lower()

def temiz(s):
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'(\w)- (\w)', r'\1\2', s)

def alinti_cikar(metin, bas, son, sinir=330):
    """Anma konumunu (bas..son) içeren cümleyi döndürür; uzunsa anmayı ortalayan pencere."""
    # Cümle sınırı ararken sayı içindeki noktaları (5.1.1 gibi kodlar) atla
    def geri_nokta(p):
        while p > 0:
            p = metin.rfind('.', 0, p)
            if p <= 0: return -1
            oncesi = metin[p-1] if p else ''
            sonrasi = metin[p+1] if p + 1 < len(metin) else ''
            if not (oncesi.isdigit() and (sonrasi.isdigit() or sonrasi in ' \n')):
                return p
        return -1
    c_bas = max(geri_nokta(bas), metin.rfind('\n\n', 0, bas))
    c_son = metin.find('.', son)
    c_bas = 0 if c_bas < 0 else c_bas + 1
    c_son = len(metin) if c_son < 0 else c_son + 1
    parca = re.sub(r'^\d+(?:\.\d+)*\.?\s+(?=[A-ZÇĞİÖŞÜ])', '', temiz(metin[c_bas:c_son]))
    if len(parca) <= sinir:
        return parca
    # anmayı ortala
    orta = temiz(metin[c_bas:bas])
    kaydir = max(0, len(orta) - sinir // 2)
    kirp = parca[kaydir:kaydir + sinir]
    return ('…' if kaydir else '') + kirp.strip() + '…'

cikti_kopru = defaultdict(lambda: defaultdict(list))   # kod -> hedef -> [kanıt]
tema_kopru = defaultdict(lambda: defaultdict(list))    # "ders|sinif|tema" -> hedef -> [kanıt]
istat = defaultdict(int)
bolum_istat = defaultdict(int)
kapsam = defaultdict(int)

for stem, ders, tam_pat, kisa_pat in PROGRAMLAR:
    yol = os.path.join(DIR, stem + '.txt')
    if not os.path.exists(yol):
        print('  ! metin yok, atlanıyor:', stem); continue
    metin = re.sub(r'(?m)^\s*\d{1,3}\s*$', '', open(yol, encoding='utf-8').read())

    saatler = [m.start() for m in re.finditer(r'DERS SAATİ', metin)]
    for i, s in enumerate(saatler):
        son = saatler[i + 1] - 200 if i + 1 < len(saatler) else min(len(metin), s + 40000)
        blok = metin[s:son]
        if len(blok) > 60000: continue
        if 'Temel Kabuller' not in blok and 'Köprü Kurma' not in blok: continue

        # olay çizelgesi: bölüm başlıkları ve çıktı kodları
        olaylar = []
        for m in BOLUM_RE.finditer(blok):
            olaylar.append((m.start(), 'bolum', BOLUM_AD[m.lastgroup]))
        onek = tam_pat.split('\\.')[0].replace('\\', '')
        for m in re.finditer(tam_pat, blok):
            olaylar.append((m.start(), 'kod', m.group(0)))
        if kisa_pat:
            for m in re.finditer(r'(?m)(?:^|\s)(' + kisa_pat + r')\.?(?=\s|$)', blok):
                olaylar.append((m.start(1), 'kod', onek + '.' + m.group(1)))
        if not olaylar: continue
        olaylar.sort()

        # bloğun ait olduğu tema (en sık geçen kodun tema anahtarı)
        kodlar = [v for _, tip, v in olaylar if tip == 'kod']
        if not kodlar: continue

        dblok = trlow(blok)
        for hedef, kalip in DERS_KALIP:
            if hedef == ders: continue
            for m in re.finditer(kalip, dblok):
                pencere = dblok[max(0, m.start() - 90):m.end() + 90]
                if not BAGLAM.search(pencere): continue
                alinti = alinti_cikar(blok, m.start(), m.end())
                if len(alinti) < 25: continue
                if re.search(r'DİSİPLİNLER ARASI|BECERİLER ARASI|PROGRAMLAR ARASI|ALAN\s*BECERİLERİ|KAVRAMSAL\s*BECERİLER', alinti):
                    continue
                harf = [c for c in alinti if c.isalpha()]
                if harf and sum(c.isupper() for c in harf) / len(harf) > 0.45: continue

                # anmadan önceki en yakın olay: bölüm mü, çıktı kodu mu?
                oncekiler = [o for o in olaylar if o[0] <= m.start()]
                if not oncekiler: continue
                poz, tip, deger = oncekiler[-1]
                son_bolum = next((o[2] for o in reversed(oncekiler) if o[1] == 'bolum'), '')

                if tip == 'kod':
                    # Bir çıktı koduyla açılan bölge yalnız iki yerde olur:
                    # (a) temanın başındaki çıktı listesi, (b) çıktı bazlı uygulama metinleri.
                    # Bazı programlarda (ör. Fen) "Öğrenme-Öğretme Uygulamaları" başlığı
                    # metne hiç düşmez; bu yüzden bölüm adı başlığa değil, konuma bakılarak
                    # belirlenir. Aksi hâlde uygulama metni bir önceki başlığın (Köprü Kurma)
                    # adıyla yanlış etiketlenir.
                    ilk_bolum = next((o[0] for o in olaylar if o[1] == 'bolum'), None)
                    son_bolum = ('Öğrenme Çıktısı metni'
                                 if ilk_bolum is not None and poz < ilk_bolum
                                 else 'Öğrenme-Öğretme Uygulamaları')
                kayit = {'a': alinti, 'o': son_bolum}
                if tip == 'kod':
                    # çıktı kodu, bölüm başlığından sonra geliyorsa bölüm çıktı bazlı demektir
                    if all(x['a'] != alinti for x in cikti_kopru[deger][hedef]):
                        cikti_kopru[deger][hedef].append(kayit)
                        istat[ders + ' → ' + hedef] += 1
                        bolum_istat[son_bolum or '(belirsiz)'] += 1
                        kapsam['çıktıya bağlandı'] += 1
                else:
                    anahtar = (ders, deger, tuple(sorted(set(kodlar))))
                    if all(x['a'] != alinti for x in tema_kopru[anahtar][hedef]):
                        tema_kopru[anahtar][hedef].append(kayit)
                        kapsam['tema düzeyinde kaldı'] += 1
                break

# --- çıktı kodlarını gerçek çıktılarla eşleştir
ck = {c['code']: c for c in json.load(open(os.path.join(VERI, 'ogrenme-ciktilari.json'), encoding='utf-8'))}
out = {}
for kod, hedefler in cikti_kopru.items():
    if kod not in ck: continue
    c = ck[kod]
    out[kod] = {'ders': c['ders'], 'sinif': c['sinif'], 'temaNo': c['temaNo'], 'tema': c['tema'],
                'statement': c['statement'], 'kopru': {h: v[:2] for h, v in hedefler.items()}}

# --- tema düzeyi köprüleri tema anahtarına bağla (bloktaki kodlardan)
tema_out = {}
for (ders, bolum, kodlar), hedefler in tema_kopru.items():
    ilk = next((ck[k] for k in kodlar if k in ck), None)
    if not ilk: continue
    anahtar = f"{ilk['ders']}|{ilk['sinif']}|{ilk['temaNo']}"
    kayit = tema_out.setdefault(anahtar, {'ders': ilk['ders'], 'sinif': ilk['sinif'],
                                          'temaNo': ilk['temaNo'], 'tema': ilk['tema'], 'kopru': {}})
    for h, v in hedefler.items():
        kayit['kopru'].setdefault(h, [])
        for x in v[:2]:
            if all(y['a'] != x['a'] for y in kayit['kopru'][h]):
                kayit['kopru'][h].append(x)

json.dump(out, open(os.path.join(VERI, 'cikti-duzeyi-kopruler.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(tema_out, open(os.path.join(VERI, 'tema-duzeyi-kopruler.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print('ÇIKTIYA BAĞLANAN köprüler :', sum(len(v['kopru']) for v in out.values()),
      f'({len(out)} çıktı)')
print('TEMA düzeyinde kalanlar   :', sum(len(v['kopru']) for v in tema_out.values()),
      f'({len(tema_out)} tema)')
print('--- çıktıya bağlananların doğduğu bölüm ---')
for k, n in sorted(bolum_istat.items(), key=lambda x: -x[1]):
    print(f'{n:4}  {k}')
print('--- en sık ders çiftleri (çıktı düzeyi) ---')
for k, n in sorted(istat.items(), key=lambda x: -x[1])[:10]:
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
