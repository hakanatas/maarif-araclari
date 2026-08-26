# Maarif Araç Kutusu

Türkiye Yüzyılı Maarif Modeli'nin **resmî ortaokul öğretim programları** makine tarafından okunabilir hâle getirildi; üzerine öğretmenin günlük işini kısaltan dört araç kuruldu. Hepsi tek bir HTML dosyasıdır: tarayıcıda çalışır, kurulum, sunucu ve üyelik istemez.

> **Resmî değildir.** Bu depo MEB tarafından hazırlanmamış, onaylanmamıştır. Metinler otomatik ayrıştırma ile çıkarıldığından eksik veya hatalı aktarım olabilir. Bağlayıcı olan, [tymm.meb.gov.tr](https://tymm.meb.gov.tr) üzerindeki resmî PDF'lerdir.

## Araçlar

| Araç | Ne işe yarar | Veri |
|---|---|---|
| 🧭 **[Kod Pusulası](araclar/kod-pusulasi.html)** | `SDB2.2`, `KB2.14`, `D14.1` gibi kodların tanımı, süreç bileşenleri, göstergeleri ve hangi derste kaç kez geçtiği | 444 kod |
| 🗺️ **[Kazanım Gezgini](araclar/kazanim-gezgini.html)** | 15 dersin bütün öğrenme çıktıları; ders/sınıf/tema filtresi, arama, süreç bileşenleri | 1256 çıktı |
| 📋 **[Ders Planı Atölyesi](araclar/ders-plani.html)** | Tema seçince 8 ögeli plan resmî metinle dolar; düzenlenir, yazdırılır | 274 tema |
| 🕸️ **[Disiplinler Arası Harita](araclar/disiplinler-haritasi.html)** | Dersler arası köprü ağı; köprüyü doğuran çıktı, program alıntısı ve plan ögesi | 192 tema, 90 çıktı köprüsü |

Açılış sayfası: [`index.html`](index.html)

## Yayına alma (GitHub Pages)

Depoyu GitHub'a gönderdikten sonra: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / `(root)`**. Birkaç dakika içinde site `https://<kullanıcı-adı>.github.io/<depo-adı>/` adresinde yayına girer.

Yerelde denemek için dosyaları çift tıklamanız yeterlidir; sunucu gerekmez.

## Depo yapısı

```
index.html              açılış sayfası
araclar/                yayına hazır uygulamalar (üretilmiş dosyalar)
veri/                   ayrıştırmayla üretilen JSON veri setleri
scriptler/              ayrıştırıcılar ve site derleyicisi
  00_kaynaklari_indir.py        resmî kaynaklar     → kaynak/
  01_beceriler.py               beceri çerçeveleri  → veri/beceriler.json
  02_ogrenme_ciktilari.py       öğrenme çıktıları   → veri/ogrenme-ciktilari.json
  03_temalar.py                 tema blokları       → veri/temalar.json
  04_cikti_duzeyi_kopruler.py   köprüler            → veri/{cikti,tema}-duzeyi-kopruler.json
  05_uygulamalari_uret.py       şablon + veri       → araclar/*.html
  sablonlar/                    veri gömülmemiş HTML şablonları
```

## Veri nasıl üretildi?

Kaynak: [tymm.meb.gov.tr](https://tymm.meb.gov.tr) üzerindeki resmî beceri çerçevesi sayfaları ve 15 ortaokul öğretim programı PDF'i (Ağustos 2026).

1. **Beceri çerçeveleri** sitenin HTML sayfalarından ayrıştırılır — PDF eklerindeki tablolar metne çevrildiğinde bozulduğu için.
2. **Öğrenme çıktıları** program PDF'lerinden çıkarılır. Her dersin kendi kod dili vardır: Fen Bilimleri beş parçalı kod kullanır (`FB.5.1.1.1`), seçmeli dersler sınıf yerine düzeyle (`GKN.1.1.1`), Türkçe ise dört sınıfı tek satırda birleştiren kod zincirleriyle (`T.O.5.1. / T.O.6.1. / …`).
3. **Tema blokları** "DERS SAATİ" çapasıyla bulunur; sekiz ögeli öğretim döngüsü (temel kabuller, ön değerlendirme, köprü kurma, uygulamalar, öğrenme kanıtları, farklılaştırma) etiket etiket kesilir.
4. **Köprüler**: bir dersin adının anıldığı cümle, tema bloğu içindeki konumuna göre sınıflandırılır. Cümle bir öğrenme çıktısının kendi uygulama metnindeyse o çıktıya bağlanır (69 çıktı, 90 bağ); temanın geneline ait bir bölümdeyse (Köprü Kurma, Ön Değerlendirme, Temel Kabuller, Farklılaştırma) hiçbir çıktıya bağlanmaz, tema düzeyinde kaydedilir (23 bağ).

Bu ayrım şart: tema geneli bölümler çıktı listesinden **sonra** geldiği için naif bir bölütleme onları listedeki son çıktıya yapıştırır ve olmayan bir bağ üretir. Ayrıca bazı programlarda (ör. Fen Bilimleri) "Öğrenme-Öğretme Uygulamaları" başlığı metne hiç düşmez; bölüm adı bu yüzden başlığa değil, konuma bakılarak belirlenir.

## Yeniden üretme

PDF'ler telif nedeniyle depoya dahil edilmemiştir; `00_kaynaklari_indir.py` bunları resmî siteden indirip `kaynak/metin/` altına metne çevirir (curl ve poppler-utils gerekir).

```bash
# 1) Resmî kaynakları indirin
python3 scriptler/00_kaynaklari_indir.py

# 2) Veriyi yeniden üretin
python3 scriptler/01_beceriler.py
python3 scriptler/02_ogrenme_ciktilari.py
python3 scriptler/03_temalar.py
python3 scriptler/04_cikti_duzeyi_kopruler.py

# 3) Uygulamaları derleyin
python3 scriptler/05_uygulamalari_uret.py
```

Yalnız arayüzü değiştirecekseniz `scriptler/sablonlar/` altındaki şablonu düzenleyip 3. adımı çalıştırmanız yeterlidir.

## Kapsam ve bilinen sınırlar

- İngilizce, Almanca ve Çoklu Yabancı Dil programları farklı yapıda olduğu için bu sürümün dışındadır.
- Fen Bilimleri ve Teknoloji-Tasarım programlarında tema düzeyi "Disiplinler Arası İlişkiler" satırı ayrıştırılamamıştır; bu iki ders haritada giden bağlantılarını çıktı düzeyi katmandan kazanır.
- Köprü katmanı ders adının metinde anılmasına dayanır; adı geçmeden kurulan ilişkiler yakalanmaz. Sayılar bu yüzden bir **alt sınırdır**.
- Haritadaki "beceri-değer dokusu örtüşen temalar" listesi resmî bir ilişki değil, türetilmiş bir benzerlik ölçüsüdür. Kodlar programlarda kimi yerde grup (`OB1`), kimi yerde alt düzeyde (`OB1.2`) yazıldığı için akraba temalar eşleşmeyebilir.
- 274 temanın 247'sinde beş çekirdek plan ögesi eksiksiz ayrıştı; kalanlarda eksik bölüm arayüzde gösterilmez.

## Lisans

Araçların kodu ve ayrıştırıcılar [MIT](LICENSE) lisansıyla açıktır. `veri/` altındaki dosyalar MEB'in resmî belgelerinden türetilmiştir; kaynak belgelerin telif hakkı Millî Eğitim Bakanlığı'na aittir.
