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
    # --- ilkokul (Eylül 2026 genişlemesi) ---
    'Ilkokul_Turkce_1-4_Ogretim_Programi': '/assets/pdf/ilkokul-turkce-dersi_20260902_111433_940.pdf',
    'Ilkokul_Matematik_1-4_Ogretim_Programi': '/assets/pdf/ilkokul-matematik-dersi_20260902_111356_122.pdf',
    'Hayat_Bilgisi_Ogretim_Programi': '/assets/pdf/hayat-bilgisi-dersi_20260902_111246_099.pdf',
    'Insan_Haklari_Vatandaslik_ve_Demokrasi_Ogretim_Programi': '/assets/pdf/2024programvat4Onayli.pdf',
    'Beden_Egitimi_ve_Oyun_Ogretim_Programi': '/assets/pdf/beden-egitimi-ve-oyun-programi.pdf',
    # --- site tarama genişlemesi (Eylül 2026): 17 seçmeli + Trafik Güvenliği.
    # Okul Öncesi programı bilinçli olarak dışarıda: ders/tema/çıktı yapısı yok.
    'Trafik_Guvenligi_Ogretim_Programi': '/assets/pdf/trafik-guvenligi-programi-tegm.pdf',
    'Secmeli_Kurani_Kerim_Ogretim_Programi': '/assets/pdf/kuran-i-kerim-dersi_20260902_110338_869.pdf',
    'Secmeli_Peygamberimizin_Hayati_Ogretim_Programi': '/assets/pdf/peygamberimizin-hayati-dersi_20260902_110804_873.pdf',
    'Secmeli_Afet_Bilinci_Ogretim_Programi': '/assets/pdf/afet-bilinci-dersi_20260819_065745_171.pdf',
    'Secmeli_Ahlak_ve_Vatandaslik_Egitimi_Ogretim_Programi': '/assets/pdf/ahlak-ve-vatandaslik-egitimi-dersi_20260819_070330_389.pdf',
    'Secmeli_Dijital_Sanatlar_Ogretim_Programi': '/assets/pdf/dijital-sanatlar-dersi_20260819_070938_522.pdf',
    'Secmeli_Dusunme_Egitimi_Ogretim_Programi': '/assets/pdf/dusunme-egitimi-dersi_20260819_071101_966.pdf',
    'Secmeli_Geleneksel_Sanatlar_Ogretim_Programi': '/assets/pdf/geleneksel-sanatlar-dersi_20260819_071232_389.pdf',
    'Secmeli_Matematik_ve_Bilim_Uygulamalari_Ogretim_Programi': '/assets/pdf/matematik-ve-bilim-uygulamalari-dersi_20260819_072414_252.pdf',
    'Secmeli_Oyun_Drama_Ogretim_Programi': '/assets/pdf/oyun-ve-oyun-etkinlikleri-dersi-drama_20260819_073410_377.pdf',
    'Secmeli_Oyun_Zeka_Oyunlari_Ogretim_Programi': '/assets/pdf/oyun-ve-oyun-etkinlikleri-dersi-zeka-oyunlari_20260819_073852_194.pdf',
    'Secmeli_Oyun_Satranc_Ogretim_Programi': '/assets/pdf/oyun-ve-oyun-etkinlikleri-dersi-santranc_20260819_073719_347.pdf',
    'Secmeli_Oyun_Geleneksel_Oyunlar_Ogretim_Programi': '/assets/pdf/oyun-ve-oyun-etkinlikleri-dersi-geleneksel-oyunlar_20260819_073604_446.pdf',
    'Secmeli_Robotik_Kodlama_Ogretim_Programi': '/assets/pdf/robotik-kodlama-dersi_20260819_074141_399.pdf',
    'Secmeli_Yapay_Zeka_Uygulamalari_Ogretim_Programi': '/assets/pdf/yapay-zeka-uygulamalari-dersi_20260819_080024_885.pdf',
    'Secmeli_Proje_Tasarimi_ve_Uygulamalari_Ogretim_Programi': '/assets/pdf/proje-tasarimi-ve-uygulamalari-dersi_20260819_074038_150.pdf',
    'Secmeli_Spor_ve_Fiziki_Etkinlikler_Ogretim_Programi': '/assets/pdf/spor-ve-fiziki-etkinlikler-dersi_20260819_075451_091.pdf',
    'Secmeli_Halk_Oyunlari_Ogretim_Programi': '/assets/pdf/halk-oyunlari-dersi_20260819_071852_879.pdf',
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
