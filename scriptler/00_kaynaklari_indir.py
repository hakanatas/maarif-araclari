#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resmî kaynakları tymm.meb.gov.tr adresinden indirir ve metne çevirir.

Kullanım:  python3 scriptler/00_kaynaklari_indir.py
Çıktı:     kaynak/beceri_html/*.html   (beceri çerçevesi sayfaları)
           kaynak/pdf/*.pdf            (öğretim programları)
           kaynak/metin/*.txt          (pdftotext -layout çıktısı)

Gereksinim: curl ve poppler-utils (pdftotext).
Belgelerin telif hakkı Millî Eğitim Bakanlığı'na aittir; bu depoya dahil edilmez.
"""
import os, subprocess, sys, time

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'kaynak')
HTML_DIR = os.path.join(KAYNAK, 'beceri_html')
PDF_DIR = os.path.join(KAYNAK, 'pdf')
METIN_DIR = os.path.join(KAYNAK, 'metin')
KOK_URL = 'https://tymm.meb.gov.tr'

BECERI_SAYFALARI = [
    ('kavramsal-beceriler', '/beceriler/kavramsal-beceriler'),
    ('egilimler', '/beceriler/egilimler'),
    ('sosyal-duygusal-ogrenme-becerileri', '/beceriler/sosyal-duygusal-ogrenme-becerileri'),
    ('erdem-deger-eylem-cercevesi', '/beceriler/erdem-deger-eylem-cercevesi'),
    ('okuryazarlik-becerileri', '/beceriler/okuryazarlik-becerileri'),
    ('fiziksel-beceriler', '/beceriler/fiziksel-beceriler'),
    ('alan-becerileri', '/alan-becerileri'),
]
ALAN_BECERILERI = ['turkce', 'matematik', 'fen-bilimleri', 'sosyal-bilimler', 'sanat',
                   'beden-egitimi-oyun-ve-spor', 'bilisim-teknolojileri-ve-yazilim',
                   'tasarim', 'din-egitimi-ve-ogretimi', 'yabanci-dil']

# ayrıştırıcıların beklediği dosya adı  ->  sitedeki PDF yolu
PROGRAMLAR = {
    'Turkce_5-8_Ogretim_Programi': '/assets/pdf/2024programtur5678Onayli.pdf',
    'Matematik_5-8_Ogretim_Programi': '/assets/pdf/2024programmat5678Onayli.pdf',
    'Fen_Bilimleri_3-8_Ogretim_Programi': '/assets/pdf/2024programfen345678Onayli.pdf',
    'Sosyal_Bilgiler_4-7_Ogretim_Programi': '/assets/pdf/2024programsos4567Onayli.pdf',
    'Din_Kulturu_ve_Ahlak_Bilgisi_4-8_Ogretim_Programi': '/assets/pdf/2024programdin45678Onayli.pdf',
    'TC_Inkilap_Tarihi_ve_Ataturkculuk_8_Ogretim_Programi': '/assets/pdf/2024programink8Onayli.pdf',
    'Ingilizce_2-8_Ogretim_Programi': '/assets/pdf/ingilizce-dersi-2-8.pdf',
    'Coklu_Yabanci_Dil_Modeli_Ingilizce': '/assets/pdf/coklu-yabanci-dil-egitim-modeli-ingilizce.pdf',
    'Coklu_Yabanci_Dil_Modeli_Almanca': '/assets/pdf/almanca-tegm.pdf',
    'Bilisim_Teknolojileri_ve_Yazilim_Ogretim_Programi': '/assets/pdf/bilisim-teknolojileri-ve-yazilim-tegm.pdf',
    'Teknoloji_ve_Tasarim_7-8_Ogretim_Programi': '/assets/pdf/teknoloji-tasarim-dersi-ogretim-programi-7-8.pdf',
    'Beden_Egitimi_ve_Spor_Ogretim_Programi': '/assets/pdf/beden-egitimi-ve-spor-tegm.pdf',
    'Gorsel_Sanatlar_Ogretim_Programi': '/assets/pdf/gorsel-sanatlar-ogretim-programi-temel-egitim.pdf',
    'Muzik_Ogretim_Programi': '/assets/pdf/muzik-dersi-programi-tegm.pdf',
    'Secmeli_Gorgu_Kurallari_ve_Nezaket_Ogretim_Programi':
        '/assets/pdf/gorgu-kurallari-ve-nezaket-dersi_20260819_071525_341.pdf',
    'Secmeli_Masal_ve_Destanlarimiz_Ogretim_Programi':
        '/assets/pdf/masal-ve-destanlarimiz-dersi_20260819_072649_012.pdf',
    'Secmeli_Okuma_Becerileri_Ogretim_Programi':
        '/assets/pdf/okuma-becerileri-dersi_20260819_073100_538.pdf',
    'Secmeli_Yazarlik_ve_Yazma_Becerileri_Ogretim_Programi':
        '/assets/pdf/yazarlik-ve-yazma-becerileri-dersi_20260819_080157_403.pdf',
}


def indir(url, hedef, deneme=3):
    if os.path.exists(hedef) and os.path.getsize(hedef) > 1024:
        return True
    for i in range(deneme):
        r = subprocess.run(['curl', '-sSL', '--max-time', '300', '-o', hedef, url],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(hedef) and os.path.getsize(hedef) > 1024:
            return True
        time.sleep(2 + 3 * i)
    print('  ! indirilemedi:', url)
    return False


def main():
    for d in (HTML_DIR, PDF_DIR, METIN_DIR):
        os.makedirs(d, exist_ok=True)

    print('Beceri çerçevesi sayfaları…')
    for ad, yol in BECERI_SAYFALARI:
        indir(KOK_URL + yol, os.path.join(HTML_DIR, ad + '.html'))
    for ad in ALAN_BECERILERI:
        indir(KOK_URL + f'/beceriler/{ad}-alan-becerileri',
              os.path.join(HTML_DIR, f'ab-{ad}.html'))
    print(f'  {len(os.listdir(HTML_DIR))} sayfa hazır')

    if subprocess.run(['which', 'pdftotext'], capture_output=True).returncode != 0:
        sys.exit('HATA: pdftotext bulunamadı. Kurulum: apt-get install poppler-utils')

    print('Öğretim programları…')
    for stem, yol in PROGRAMLAR.items():
        pdf = os.path.join(PDF_DIR, stem + '.pdf')
        txt = os.path.join(METIN_DIR, stem + '.txt')
        if not indir(KOK_URL + yol, pdf):
            continue
        if not os.path.exists(txt):
            subprocess.run(['pdftotext', '-layout', pdf, txt], capture_output=True)
        print(f'  {stem[:52]:54} {os.path.getsize(pdf)/1e6:5.1f} MB')

    print('\nHazır. Sıradaki adım:  python3 scriptler/01_beceriler.py')


if __name__ == '__main__':
    main()
