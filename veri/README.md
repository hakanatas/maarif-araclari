# Veri setleri

Tümü [tymm.meb.gov.tr](https://tymm.meb.gov.tr) üzerindeki resmî belgelerden otomatik ayrıştırmayla üretilmiştir (Ağustos 2026; ilkokul programları Eylül 2026'da eklendi).

| Dosya | İçerik | Üreten |
|---|---|---|
| `beceriler.json` | 444 beceri/değer/eğilim kodu: tanım, süreç bileşenleri, göstergeler | `01_beceriler.py` |
| `beceri-kullanim.json` | Her kodun hangi derste kaç kez geçtiği (312 kod) | `01_beceriler.py` |
| `ogrenme-ciktilari.json` | 2107 öğrenme çıktısı: kod, ders, sınıf, tema, ifade, süreç bileşenleri | `02_ogrenme_ciktilari.py` |
| `temalar.json` | 539 tema bloğu: ders saati, beceri satırları, 8 ögeli öğretim döngüsü | `03_temalar.py` |
| `cikti-duzeyi-kopruler.json` | 109 öğrenme çıktısının kendi uygulama metninde belgelenmiş 134 köprü + kanıt cümlesi | `04_cikti_duzeyi_kopruler.py` |
| `tema-duzeyi-kopruler.json` | Temanın geneline ait bölümlerde geçen, belirli bir çıktıya bağlanamayan 48 köprü ifadesi | `04_cikti_duzeyi_kopruler.py` |
| `harita.json` | Haritanın kullandığı birleşik veri (temalar + kod sözlüğü + köprüler) | `04` sonrası birleştirme |
| `surum.json` | Üretim tarihi, kaç belgeden üretildiği ve kayıt sayıları — sayfaların altındaki damga | `06_kaynak_denetimi.py` |
| `kaynak-imzalari.json` | Her kaynağın parmak izi: yerel metin özeti + uzak HTTP başlıkları (`etag`, `last-modified`, `content-length`). Tazelik denetiminin ölçütüdür | `06_kaynak_denetimi.py` |

Kaynak belgelerin telif hakkı Millî Eğitim Bakanlığı'na aittir.
