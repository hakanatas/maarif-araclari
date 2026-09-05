# Maarif Araç Kutusu

Türkiye Yüzyılı Maarif Modeli'nin **resmî ilkokul ve ortaokul öğretim programları** (1-8. sınıf) makine tarafından okunabilir hâle getirildi; üzerine öğretmenin günlük işini kısaltan beş araç kuruldu. Hepsi tek bir HTML dosyasıdır: tarayıcıda çalışır, kurulum, sunucu ve üyelik istemez.

> **Resmî değildir.** Bu depo MEB tarafından hazırlanmamış, onaylanmamıştır. Metinler otomatik ayrıştırma ile çıkarıldığından eksik veya hatalı aktarım olabilir. Bağlayıcı olan, [tymm.meb.gov.tr](https://tymm.meb.gov.tr) üzerindeki resmî PDF'lerdir.

## Araçlar

| Araç | Ne işe yarar | Veri |
|---|---|---|
| 🧭 **[Kod Pusulası](araclar/kod-pusulasi.html)** | `SDB2.2`, `KB2.14`, `D14.1` gibi kodların tanımı, süreç bileşenleri, göstergeleri ve hangi derste kaç kez geçtiği | 444 kod |
| 🗺️ **[Kazanım Gezgini](araclar/kazanim-gezgini.html)** | 36 dersin bütün öğrenme çıktıları, 1. sınıftan 8. sınıfa, bütün seçmeliler dahil; ders/sınıf/tema filtresi, arama, süreç bileşenleri | 2107 çıktı |
| 📋 **[Ders Planı Atölyesi](araclar/ders-plani.html)** | Tema seçince 8 ögeli plan resmî metinle dolar; düzenlenir, yazdırılır | 539 tema |
| 🕸️ **[Disiplinler Arası Harita](araclar/disiplinler-haritasi.html)** | **Ders ağı** (ağ ya da matris olarak; üstüne gelince bağlar öne çıkar, düğümler sürüklenir, "sınıfları oynat" ile ağın sınıf düzeyine göre değişimi izlenir). Her köprü temaya, tema kendi öğrenme çıktılarına, çıktı da süreç bileşenlerine kadar açılır + roller ve kapsama · **Ortak beceriler**: iki programın aynı kodu nerede çalıştığı; kod türüne göre süzülebilir (kavramsal / sosyal-duygusal / okuryazarlık / değer / eğilim) ve iki düzeyde bakılabilir — temalar (36 dersin hepsi) ya da öğrenme çıktıları (etiket yalnız 279 çıktıda var, 204'ü Türkçe) · **Yıl takvimi** · **Ara ve raporla**: bütün katmanlarda arama ve yazdırılabilir zümre raporu | 539 tema, 134 çıktı köprüsü, 48 tema geneli köprü |
| 📊 **[Beceri Gelişim Panosu](araclar/beceri-panosu.html)** | Öğrenci × süreç bileşeni izleme matrisi; sınıfın hangi bileşende takıldığını ve kimin desteğe ihtiyacı olduğunu gösterir. Veri yalnız tarayıcıda kalır, JSON olarak yedeklenir | 2107 çıktının süreç bileşenleri |

Açılış sayfası: [`index.html`](index.html) · Öğretmenlere yönelik kullanım rehberi: [`kullanim.html`](kullanim.html) — dağıtmak için A4 sürümü: [`Maarif-Arac-Kutusu-Rehberi.pdf`](Maarif-Arac-Kutusu-Rehberi.pdf)

### Yapay zekâ istemleri

Statik bir site metin üretemez — ama üretecek olana verilecek **istemi** hazırlayabilir. Ders Planı Atölyesi'nin sonunda yedi istem türü vardır (ölçme aracı, analitik rubrik, destekleme, zenginleştirme, ön değerlendirme, köprü etkinliği, veli bilgilendirme). İstem, temanın programdaki kendi cümleleri ve sizin işaretlediğiniz çıktıların süreç bileşenleriyle kurulur; kopyalayıp herhangi bir yapay zekâ sohbetine yapıştırırsınız. Beceri Gelişim Panosu ise tuttuğunuz gözlemden bir **destekleme istemi** üretir: sınıfın en zayıf süreç bileşenleri ve kaç öğrencinin geride olduğu isteme girer, öğrenci adları girmez.

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
  05_uygulamalari_uret.py       şablon + veri       → araclar/*.html, kullanim.html
  06_kaynak_denetimi.py         tazelik denetimi    → veri/surum.json, veri/kaynak-imzalari.json
  07_yazitipi_gom.py            yazı tipi gömme     → sablonlar/yazitipleri.css (bir kez, ağ ister)
  07_rehber_pdf.mjs             rehberi A4 bas      → Maarif-Arac-Kutusu-Rehberi.pdf
  08_tutarlilik_denetimi.py     tutarlılık denetimi → çapraz referanslar + anlatı sayıları
  sablonlar/                    veri gömülmemiş HTML şablonları
                                (kullanim.sablon.html veri almaz; kök dizindeki rehber sayfasına derlenir)
  sablonlar/gorseller/          rehberdeki ekran görüntüleri (derlemede data URI olarak gömülür)
```

## Veri nasıl üretildi?

Kaynak: [tymm.meb.gov.tr](https://tymm.meb.gov.tr) üzerindeki resmî beceri çerçevesi sayfaları ile 38 öğretim programı PDF'i: 15 ortaokul çekirdek + seçmeli, 5 ilkokul (İlkokul Türkçe, İlkokul Matematik, Hayat Bilgisi, İnsan Hakları Vatandaşlık ve Demokrasi, Beden Eğitimi ve Oyun) ve sitenin program kataloğu taranarak eklenen 18 belge daha (Trafik Güvenliği ile Kur'an-ı Kerim, Peygamberimizin Hayatı, Afet Bilinci, Dijital Sanatlar, Düşünme Eğitimi, Geleneksel Sanatlar, Matematik ve Bilim Uygulamaları, dört Oyun ve Oyun Etkinlikleri modülü, Robotik Kodlama, Yapay Zekâ Uygulamaları, Proje Tasarımı, Spor ve Fiziki Etkinlikler, Halk Oyunları seçmelileri — Eylül 2026). Türkçe ve Matematik'in ilkokul programları ortaokuldakiyle aynı ders adında birleşir; Fen Bilimleri 3-8 ve Görsel Sanatlar 1-8 nasıl tek dersse bunlar da öyle.

1. **Beceri çerçeveleri** sitenin HTML sayfalarından ayrıştırılır — PDF eklerindeki tablolar metne çevrildiğinde bozulduğu için.
2. **Öğrenme çıktıları** program PDF'lerinden çıkarılır. Her dersin kendi kod dili vardır: Fen Bilimleri beş parçalı kod kullanır (`FB.5.1.1.1`), seçmeli dersler sınıf yerine düzeyle (`GKN.1.1.1`), Türkçe ise dört sınıfı tek satırda birleştiren kod zincirleriyle (`T.O.5.1. / T.O.6.1. / …`).
3. **Tema blokları** "DERS SAATİ" çapasıyla bulunur; sekiz ögeli öğretim döngüsü (temel kabuller, ön değerlendirme, köprü kurma, uygulamalar, öğrenme kanıtları, farklılaştırma) etiket etiket kesilir.
4. **Tema çıktıları**: her tema, kendi öğrenme çıktılarının kod, ifade ve süreç bileşeni listesiyle birlikte haritaya girer; böylece bir köprüden çıktı düzeyine inmek için araç değiştirmek gerekmez. Türkçe'de çıktılar temalara değil beceri alanlarına bağlı olduğundan o temalar listesiz kalır ve arayüz bunu ayrıca söyler.
5. **Köprüler**: bir dersin adının anıldığı cümle, tema bloğu içindeki konumuna göre sınıflandırılır. Cümle bir öğrenme çıktısının kendi uygulama metnindeyse o çıktıya bağlanır (69 çıktı, 90 bağ); temanın geneline ait bir bölümdeyse (Köprü Kurma, Ön Değerlendirme, Temel Kabuller, Farklılaştırma) hiçbir çıktıya bağlanmaz, tema düzeyinde kaydedilir (23 bağ).

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
python3 scriptler/08_tutarlilik_denetimi.py   # veri ile sayfa metinleri uyuşuyor mu?

# 3) Sürüm damgasını tazeleyin (uzak denetim isteğe bağlı)
python3 scriptler/06_kaynak_denetimi.py --uzak --kaydet

# 4) Uygulamaları derleyin
python3 scriptler/05_uygulamalari_uret.py

# 5) Rehberi PDF'e basın (isteğe bağlı; playwright gerekir)
node scriptler/07_rehber_pdf.mjs
```

Rehber sayfasının yazı tipleri sayfaya gömülüdür (`scriptler/sablonlar/yazitipleri.css`), böylece sayfa çevrimdışı da doğru dizilir ve PDF'e basarken yedek yüze düşmez. Bu dosya depoda hazır durur; yalnız yazı tipi seçimi değişirse `07_yazitipi_gom.py` yeniden çalıştırılır.

### Veri güncel mi?

Her sayfanın altında verinin hangi tarihte, kaç resmî belgeden üretildiğini söyleyen bir damga vardır. Kaynakların değişip değişmediği tek komutla denetlenir:

```bash
python3 scriptler/06_kaynak_denetimi.py --uzak
```

Bu komut PDF indirmez; yalnız HTTP başlıklarına (`etag`, `last-modified`, `content-length`) bakıp ölçüt dosyasıyla karşılaştırır. Değişen belge varsa listeler ve çıkış kodu `1` döner — zamanlanmış bir denetime doğrudan bağlanabilir. Değişiklik bulunduğunda 00→05 adımları yeniden çalıştırılmalıdır.

Yalnız arayüzü değiştirecekseniz `scriptler/sablonlar/` altındaki şablonu düzenleyip son adımı çalıştırmanız yeterlidir.

## Kapsam ve bilinen sınırlar

- İngilizce, Almanca ve Çoklu Yabancı Dil programları farklı yapıda olduğu için bu sürümün dışındadır. Okul Öncesi Eğitim Programı da dışarıdadır: ders/tema/çıktı kodu yapısı taşımaz.
- MEB, `GS` kod önekini hem Görsel Sanatlar'a hem Geleneksel Sanatlar'a vermiştir; 15 kod iki derste birden vardır. Boru hattı bu yüzden kodu tek başına değil ders+kod olarak anahtarlar.
- Robotik Kodlama ve Yapay Zekâ Uygulamaları belgeleri kodu önekten sonra noktasız yazar (`RK1.1.1`); ayrıştırıcı bunları noktalı kanonik biçime çevirir.
- Fen Bilimleri 3-4. sınıfta dört parçalı kod kullanır (`FB.3.1.1`), 5-8'de beş parçalı (`FB.5.1.1.1`); ayrıştırıcı ikisini de tanır. (Bu ayrım gözden kaçtığı için 3-4. sınıf Fen çıktıları bir süre eksik yayımlandı; Eylül 2026'da düzeltildi.)
- Fen Bilimleri ve Teknoloji-Tasarım programlarında tema düzeyi "Disiplinler Arası İlişkiler" satırı ayrıştırılamamıştır; bu iki ders haritada giden bağlantılarını çıktı düzeyi katmandan kazanır.
- Köprü katmanı ders adının metinde anılmasına dayanır; adı geçmeden kurulan ilişkiler yakalanmaz. Sayılar bu yüzden bir **alt sınırdır**.
- Haritadaki "benzer temalar" listesi ve **Ortak beceriler** sekmesi resmî bir ilişki değil, türetilmiş bir ölçüdür: temaların beceri-değer kodu kesişiminden hesaplanır. Ortak kod birlikte çalışmak için bir aday gösterir, bir zorunluluk değil. Kodlar programlarda kimi yerde grup (`OB1`), kimi yerde alt düzeyde (`OB1.2`) yazıldığı için akraba temalar eşleşmeyebilir.
- Haritanın **Ara ve raporla** sekmesindeki arama tema başlıklarında, beceri kodlarında ve köprü alıntılarında çalışır; temaların tam metni bu araca yüklü değildir (o metin Ders Planı Atölyesi'ndedir).
- **Roller ve kapsama** bölümündeki "veri boşluğu" rozeti önemlidir: köprüsüz görünen temaların bir kısmı gerçekten bağlanmıyor, bir kısmı ise Fen Bilimleri ve Teknoloji-Tasarım programlarında ayrıştırılamayan satırlar yüzünden boş görünüyor.
- 539 temanın 261'inde beş çekirdek plan ögesi eksiksiz ayrıştı (2026 seçmelilerinin çoğu kısaltılmış döngü kullanır: Temel Kabuller ve Köprü Kurma bölümleri programda hiç yok); eksik bölüm arayüzde gösterilmez.
- Ağdaki düğüm konumları sınıf filtresinden bağımsızdır ve bir kez hesaplanır; böylece filtre değişince dersler yer değiştirmez ve "sınıfları oynat" sırasında yalnız bağlar belirip söner.
- Yıl takvimindeki hafta aralıkları **tahmindir**: temaların programdaki sırayla ve yazılı ders saatleriyle 36 haftalık yıla yayıldığı varsayılır. Ders adları ve saatler resmîdir, haftalara dağıtım hesaplanmıştır.
- Beceri Gelişim Panosu'ndaki değerlendirme ölçütü öğretmene aittir; pano resmî bir ölçme aracı değil, dijital bir gözlem defteridir. Veri yalnız o tarayıcıda durur — cihaz değişince taşınmaz, tarayıcı verisi silinince kaybolur; kalıcılık için "Yedek al" gerekir.
- İstem üreteci metin üretmez, istem üretir. Yapay zekânın döndürdüğü içerik resmî değildir ve çıktı kodlarıyla karşılaştırılmadan kullanılmamalıdır.
- Büyük harfli tema başlıklarında PDF font eşlemesi bazen `İ` harfini noktasız `I` yapıyor; başlıklar aynı metnin gövdesindeki doğru yazımdan otomatik onarılır (`03_temalar.py`).

## Lisans

Araçların kodu ve ayrıştırıcılar [MIT](LICENSE) lisansıyla açıktır. `veri/` altındaki dosyalar MEB'in resmî belgelerinden türetilmiştir; kaynak belgelerin telif hakkı Millî Eğitim Bakanlığı'na aittir.
