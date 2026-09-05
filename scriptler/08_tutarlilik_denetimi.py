#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veri ile anlatının tutarlılık denetimi.

Kullanım:  python3 scriptler/08_tutarlilik_denetimi.py

İki şeyi denetler:
1. Çapraz referanslar: köprü hedefleri bilinen derslere mi gidiyor, beceri
   etiketleri sözlükte var mı, tema başına çıktı sayısı listeyle uyuşuyor mu,
   ifadelerde ikilenme kalmış mı.
2. Anlatı sayıları: sayfalardaki "N öğrenme çıktısı / N tema / N köprü" gibi
   ifadeler veriden yeniden hesaplanan gerçek sayılarla uyuşuyor mu. Sayılar
   her genişlemede elle güncellendiği için bayatlamaya en açık yer burası.

Uyumsuzluk varsa listeler ve çıkış kodu 1 döner.
"""
import json, os, re, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI = os.path.join(KOK, 'veri')

def oku(ad):
    with open(os.path.join(VERI, ad), encoding='utf-8') as f:
        return json.load(f)

hatalar = []

# ---------- gerçek sayılar
ciktilar = oku('ogrenme-ciktilari.json')
temalar = oku('temalar.json')
harita = oku('harita.json')
beceriler = oku('beceriler.json')
kullanim = oku('beceri-kullanim.json')
ck = oku('cikti-duzeyi-kopruler.json')
tk = oku('tema-duzeyi-kopruler.json')
surum = oku('surum.json')

canon = {
    'cikti': len(ciktilar),
    'tema': len(temalar),
    'ders': len({c['ders'] for c in ciktilar}),
    'kod': len(beceriler),
    'kullanim_kod': len(kullanim),
    'ck_bag': sum(len(v['kopru']) for v in ck.values()),
    'ck_cikti': len({(v['ders'], v.get('kod', k)) for k, v in ck.items()}),
    'tk_bag': sum(len(v['kopru']) for v in tk.values()),
    'tk_tema': len(tk),
    'baglantili_tema': sum(1 for t in harita['temalar']
                           if t.get('hedefler') or
                           harita['ciktiKopru'].get(f"{t['ders']}|{t['sinif']}|{t['temaNo']}") or
                           harita['temaKopru'].get(f"{t['ders']}|{t['sinif']}|{t['temaNo']}")),
    'etiketli_cikti': sum(1 for c in ciktilar if c.get('refs')),
}

# ---------- 1) surum.json
for anahtar, beklenen in [('öğrenme çıktısı', canon['cikti']), ('tema', canon['tema']),
                          ('beceri kodu', canon['kod']), ('çıktı düzeyi köprü', canon['ck_bag']),
                          ('tema düzeyi köprü', canon['tk_bag'])]:
    if surum['kayitlar'].get(anahtar) != beklenen:
        hatalar.append(f"surum.json: {anahtar} = {surum['kayitlar'].get(anahtar)}, gerçek {beklenen} → 06'yı çalıştırın")

# ---------- 2) çapraz referanslar
bilinen_ders = {c['ders'] for c in ciktilar} | {t['ders'] for t in temalar}
DIS_BILINEN = {'İngilizce', 'Trafik Güvenliği'}
for t in harita['temalar']:
    for h in (t.get('hedefler') or []):
        if h not in bilinen_ders and h not in DIS_BILINEN:
            hatalar.append(f"harita hedefi bilinmeyen ders: {t['ders']} {t['sinif']}/{t['temaNo']} → {h}")

kod_kokleri = {e['code'] for e in beceriler}
eksik_ref = set()
for c in ciktilar:
    for r in (c.get('refs') or []):
        r0 = r.rstrip('.')
        if r0 not in kod_kokleri and not any(r0.startswith(k + '.') or k.startswith(r0 + '.') for k in kod_kokleri):
            eksik_ref.add(r0)
if eksik_ref:
    hatalar.append(f"sözlükte olmayan beceri etiketi ({len(eksik_ref)}): {sorted(eksik_ref)[:8]}…")

for t in harita['temalar']:
    if t.get('ciktilar') and t.get('cikti') != len(t['ciktilar']):
        hatalar.append(f"tema çıktı sayısı tutarsız: {t['ders']} {t['sinif']}/{t['temaNo']} cikti={t['cikti']} liste={len(t['ciktilar'])}")

def ikilenmis(m):
    m = m.strip(); n = len(m)
    return n >= 8 and n % 2 == 1 and m[n//2] == ' ' and m[:n//2] == m[n//2+1:]
n_ikili = sum(1 for c in ciktilar if ikilenmis(c['statement']))
if n_ikili:
    hatalar.append(f"ikilenmiş ifade: {n_ikili} çıktı")

# GS çakışması bilinçli: yalnız beklenmedik çakışmaları raporla
from collections import Counter
kodlar = Counter(c['code'] for c in ciktilar)
beklenen_cakisma_dersleri = {'Görsel Sanatlar', 'Geleneksel Sanatlar (Seçmeli)'}
for kod, n in kodlar.items():
    if n > 1:
        dersler = {c['ders'] for c in ciktilar if c['code'] == kod}
        if not dersler <= beklenen_cakisma_dersleri:
            hatalar.append(f"beklenmedik kod çakışması: {kod} → {sorted(dersler)}")

# ---------- 3) anlatı sayıları
DOSYALAR = ['index.html', 'README.md', 'veri/README.md',
            'scriptler/sablonlar/kazanim-gezgini.sablon.html',
            'scriptler/sablonlar/ders-plani.sablon.html',
            'scriptler/sablonlar/disiplinler-haritasi.sablon.html',
            'scriptler/sablonlar/kod-pusulasi.sablon.html',
            'scriptler/sablonlar/kullanim.sablon.html']
KALIPLAR = [
    (r'(\d[\d.]*)\s*öğrenme çıktısı', {canon['cikti'], canon['ck_cikti']}),
    (r'(\d+)\s*tema(?:\b|,)(?!\s*(?:geneli|düzey))', {canon['tema'], canon['baglantili_tema']}),
    (r'(\d+)\s*çıktı köprüsü', {canon['ck_bag']}),
    (r'(\d+)\s*tema geneli köprü', {canon['tk_bag']}),
    (r'(\d+)\s*dersin', {canon['ders']}),
    (r'(\d+)\s*kodun ders bazlı', {canon['kullanim_kod']}),
    # açılış sayfasının sayı karoları (markup bölünmüş biçim)
    (r'<b>(\d+)</b><span>öğrenme çıktısı', {canon['cikti']}),
    (r'<b>(\d+)</b><span>tema<', {canon['tema']}),
]
for dosya in DOSYALAR:
    yol = os.path.join(KOK, dosya)
    metin = open(yol, encoding='utf-8').read()
    for kalip, gecerli in KALIPLAR:
        for m in re.finditer(kalip, metin):
            n = int(m.group(1).replace('.', ''))
            if n not in gecerli and n > 20:   # küçük sayılar (ör. "4 tema") bağlamsaldır
                satir = metin[:m.start()].count('\n') + 1
                hatalar.append(f"{dosya}:{satir}: '{m.group(0).strip()}' — gerçek: {sorted(gecerli)}")

if hatalar:
    print('TUTARSIZLIK (%d):' % len(hatalar))
    for h in hatalar:
        print(' *', h)
    sys.exit(1)
print('Tutarlı: %d çıktı, %d tema, %d ders, %d çıktı bağı, %d tema geneli bağ, %d bağlantılı tema.'
      % (canon['cikti'], canon['tema'], canon['ders'], canon['ck_bag'], canon['tk_bag'], canon['baglantili_tema']))
