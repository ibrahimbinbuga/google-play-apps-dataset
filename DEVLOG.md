# DEVLOG: Google Play Apps 2026 | Gelir Modeli, Tür ve Kurulum Bandı

Durum: Adım 1-10 tamam (açık kararlar İbrahim'de)
Başlangıç: 2026-10-30

## Karar ve varsayımlar
- 2026-10-30 | Seviye 2 seçildi (SQL + dashboard) | Roadmap'in Seviye 2 örneği Google Play, veri tablolara bölünebilir
- 2026-10-30 | Ana soru: gelir modeli × tür × kurulum bandı | Tek cümle, SQL ile cevaplanabilir, ürün çıkarımına bağlanabilir
- 2026-10-30 | `monetization`: `free = False` ise `paid`, diğerleri reklam/IAP kombinasyonu | Ücretli uygulama tek kategoriye indirgendi
- 2026-10-30 | Veri tam verinin %9'u, geliştirici bazlı hash örneklemi | Sonuçlar tüm Google Play'e genelleştirilmez
- 2026-10-30 | Lisans BY-NC-SA 4.0 kabul edildi (varsayım) | REPORT.md "CC BY-NC 4.0", Kaggle API "CC-BY-NC-SA-4.0" diyor, daha sıkı olan esas alındı
- 2026-10-30 | `price` boş 13 satır silinmedi | Hepsi `free=False`, `monetization` için yeterli; fiyat analizinde dışarıda kalır
- 2026-10-31 | Oyun olan Sports satırları (351) `Sports (Game)` türüne ayrıldı | Sports hem oyun hem uygulama; `genres (genre PK, is_game)` şeması tek değer istiyor. İbrahim onayladı
- 2026-10-31 | Tür birleştirme yapılmadı | "Educational" ve "Music" yalnızca oyunlarda geçiyor, "Education" ve "Music & Audio"nun kopyası değil
- 2026-10-31 | `installs_min` bandın alt sınırı (varsayım) | "1,000,000+" gerçekte 1M-5M aralığı; tam sayı değil, sıralama ve gruplama için kullanılır
- 2026-10-31 | Grafiklerde 50M ve üstü bantlar birleştirildi (n=244) | Tek tek bantlarda n 1-128; yüzdeler anlamsız dalgalanıyor

## Kayıtlar

### 2026-10-30 | Adım 1: Repo iskeleti
- Yapılan: `data/`, `notebooks/`, `figures/`, `src/`, `sql/`, `app/` klasörleri açıldı (boş klasörler için `.gitkeep`). `.gitignore` yazıldı (`data/`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`, `.DS_Store`, `.streamlit/secrets.toml`). `.venv` (Python 3.15.2) kuruldu, `requirements.txt` sabit sürümlerle yazıldı: pandas 3.1.0, numpy 2.5.4, matplotlib 3.11.2, altair 6.3.0, streamlit 1.66.1, jupyter 1.1.1, ipykernel 7.4.0, nbconvert 7.17.2, kaggle 2.2.5.
- Bulunan: Proje klasörü henüz git reposu değil. `.gitignore` hazır, `git init` İbrahim'e bırakıldı.
- Sorun: Yok.
- Süre: ~10 dk
- Sonraki: Adım 2, veriyi indir ve doğrula.

### 2026-10-30 | Adım 2: Veriyi indir ve doğrula
- Yapılan: `kaggle datasets download -d fliarbi/google-play-apps-2026 -p data/ --unzip` çalıştırıldı. Zip içinden `google_play_apps_2026_sample.csv`, `REPORT.md`, `report.pdf` ve `figures/` çıktı. `src/validate.py` yazıldı (şekil, tip, eksik, tekrar, aykırı fiyat/puan, tarih tutarlılığı, kategorikler). Çıktı aşağıdaki "Veri kalite notları"na işlendi. TASK.md'deki "DOĞRULANMADI" ifadeleri ölçülen değerlerle değiştirildi.
- Bulunan:
  - 100,013 satır x 19 sütun, 20.0 MB. Tam tekrarlı satır 0, tekrarlı `app_id` 0.
  - `currency` tek değer (USD), `installs` 15 bant (en küçük "1,000+").
  - Puan yalnızca 31,755 uygulamada var (%31.75). Ücretli uygulamalarda puan oranı %65.4, ücretsizlerde %31.2: puan alt kümesi ücretli uygulamalara doğru kayık.
  - `genre` 48 değer. "Educational" (790) ve "Music" (143) yalnızca `is_game = True` satırlarda; yani bunlar Google Play'in oyun alt kategorileri, "Education"/"Music & Audio" ile aynı şey değil.
  - "Sports" hem oyun (351) hem uygulama (1,984) olarak geçiyor. Diğer 47 türde `is_game` tek değerli. Şemadaki `genres (genre PK, is_game)` tablosu bu haliyle Sports'u taşıyamaz, Adım 3/5'te karar gerekiyor.
- Sorun:
  - Lisans çelişkisi: REPORT.md "CC BY-NC 4.0", Kaggle API "CC-BY-NC-SA-4.0". Daha sıkı olan BY-NC-SA esas alındı, README'deki lisans satırı Adım 9'da güncellenecek.
  - 13 uygulamada `free = False` ama `price` boş. `monetization` için `free` yeterli (hepsi `paid`), satır silinmeyecek; fiyat analizlerinde bu 13 satır dışarıda kalır.
  - 199 uygulamada `last_updated < released` (fark medyan 30 gün, max 1,436 gün). Muhtemelen mağazanın "released" alanı yeniden yayın tarihini gösteriyor. Silinmeyecek, `days_since_update` yalnızca `last_updated`'tan hesaplandığı için ana soruyu etkilemiyor.
- Süre: ~25 dk
- Sonraki: Adım 3, temizleme ve türetilmiş sütunlar. Açık kararlar: (a) Sports oyun/uygulama ayrımı, (b) genre birleştirme yapılmaması önerisi (yukarıdaki kanıt).

### 2026-10-31 | Adım 3: Temizleme ve türetilmiş sütunlar
- Yapılan: `src/clean.py` yazıldı, çıktı `data/apps_clean.csv` (100,013 satır x 23 sütun, git dışı). `load_clean()` sonraki adımlar için tipleri koruyarak okur.
  - Sports: `is_game = True` olan 351 satır `Sports (Game)` türüne alındı (İbrahim onayladı). Artık 49 tür var ve her türde `is_game` tek değerli.
  - Tür birleştirme yapılmadı: "Educational"/"Music" oyun alt kategorisi (Adım 2 kanıtı).
  - `released`, `last_updated` datetime; `ratings`, `reviews` nullable tamsayı (`Int64`).
  - `fliar_profile_url` atıldı (analizde kullanılmıyor, Kural 10 gereği linklere gidilmiyor).
  - Türetilenler: `installs_min`, `monetization`, `is_rated`, `release_year`, `days_since_update` (referans 2026-06-08).
- Bulunan:
  - Silinen satır 0.
  - `monetization`: free_clean 49,390 (%49.38), ads_only 30,871 (%30.87), ads_iap 12,483 (%12.48), iap_only 5,793 (%5.79), paid 1,476 (%1.48).
  - Ücretli 1,476 uygulamanın 95'i reklam, 224'ü IAP da içeriyor; varsayım gereği hepsi `paid`.
  - `installs_min` 1,000 → 10,000,000,000; her bant tek bir sayıya eşleniyor.
  - `is_rated` 31,755 (%31.75). `release_year` 17,467 boş (`released` boş olanlar), aralık 2010-2026.
  - `days_since_update` 0 → 6,168, medyan 195 gün, negatif yok. 365 günden eski güncelleme %27.80 (tüm veri; banda göre kırılım Adım 6, soru 9).
- Sorun: Yok.
- Süre: ~20 dk
- Sonraki: Adım 4, örneklem sağlaması ve geliştirici yoğunlaşması.

### 2026-10-31 | Adım 4: Örneklem sağlaması ve geliştirici yoğunlaşması
- Yapılan: `src/sample_check.py` yazıldı. Reklam/IAP/ücretli oranları REPORT.md kıyas değerleriyle karşılaştırıldı. Geliştirici kimliği (developer, developer_domain) çifti olarak tanımlandı, yoğunlaşma ölçüldü. Duyarlılık için en büyük 10 geliştirici çıkarılıp oranlar yeniden hesaplandı. Düzeltme/ağırlıklandırma yapılmadı.
- Bulunan:
  - Kıyas: reklam %43.44 (tam veri %43, +0.44 puan), IAP %18.50 (%18, +0.50), ücretli %1.48 (%1.4, +0.08). Örneklem tam veriyle 1 puandan az farkla uyumlu.
  - 47,956 geliştirici; medyan 1 uygulama, ortalama 2.09, max 6,022. Geliştiricilerin %79.9'u tek uygulamalı.
  - En büyük 10 geliştiricinin payı %9.10; en büyük 100 %18.31, en büyük 1,000 %35.19.
  - En büyük "geliştirici" `Individual developer` (domain'siz, 6,022 uygulama, %6.02). Bu genel bir etiket, tek kişi değil. Hariç tutulunca en büyük 10'un payı %3.33.
  - Büyük geliştiricilerin gelir modeli tek tip: klavye/tema hesapları (Cool keyboard skin, Delicate theme, Fancy keyboard, toplam 1,053 uygulama) ~%99-100 `ads_only`; GPSmyCity (383) %100 `ads_iap`; MINDBODY (273) ve WABiz (819) ~%99-100 `free_clean`. Tür düzeyi oranları bu hesaplar kaydırabilir (örn. Personalization).
  - Duyarlılık: en büyük 10 geliştirici çıkarılınca (90,911 satır) reklam %41.99, IAP %19.09, ücretli %1.56. Genel oranlar ~1 puan oynuyor.
- Sorun: (developer, domain) anahtarı aynı şirketi bölebiliyor: "WABiz - Aplicativos para Delivery" domain'siz (534) ve `wabiz.com.br` (285) olarak iki ayrı geliştirici sayılıyor. Şema tanımı gereği değiştirilmedi, sınırlama olarak not edildi.
- Süre: ~20 dk
- Sonraki: Adım 5, SQLite şeması ve yükleme. Tür düzeyi karşılaştırmalarda büyük geliştiricilerin etkisi Adım 6'da (soru 6) ve dashboard'un yoğunlaşma sekmesinde gösterilecek.

### 2026-10-31 | Adım 5: SQLite şeması ve yükleme
- Yapılan: `sql/schema.sql` yazıldı (4 tablo: `apps`, `developers`, `genres`, `install_bands`; FK, CHECK ve 4 indeks). `src/load_db.py` temiz veriyi `data/apps.db`'ye yükler (git dışı). `developer_id` (developer, developer_domain) çiftine verilen yapay tamsayı anahtar. `band_rank` `installs_min` sırasına göre 1-15. Boolean'lar 0/1, tarihler `YYYY-MM-DD` metin.
- Bulunan:
  - Satırlar: `apps` 100,013, `developers` 47,956 (10,794'ü domain'siz), `genres` 49, `install_bands` 15.
  - `PRAGMA foreign_key_check` hatası 0. `developer_id` boş satır 0. Dört tablonun JOIN'i 100,013 satır veriyor (kayıp yok).
  - `monetization` dağılımı SQLite'ta Adım 3 ile birebir aynı.
- Sorun: Yok. Not: `developers` tablosunda (developer, NULL) çiftleri için SQLite UNIQUE kısıtı NULL'ları farklı sayar; tekilliği pandas tarafında `drop_duplicates` sağlıyor.
- Süre: ~20 dk
- Sonraki: Adım 6, 10 SQL sorusu (`sql/queries.sql`) ve notebook.
### 2026-10-31 | Adım 6: SQL soruları
- Yapılan: `sql/queries.sql` 10 soruyla yazıldı (GROUP BY, JOIN, CASE, HAVING, RANK, ROW_NUMBER, SUM OVER, CTE). `src/queries.py` dosyayı "-- Q<n>:" işaretlerine göre bölüp çalıştırır. `notebooks/analysis.ipynb` Adım 2-6'yı baştan sona çalıştırıyor (`jupyter nbconvert --execute`, 24 hücre, 0 hata).
- Bulunan (hepsi örneklem içi, nedensel değil):
  - Q1/Q8: 49 tür. En büyük tür Education (10,438, %10.44). İlk 10 tür uygulamaların %55.78'i.
  - Q2: Kurulum bandı arttıkça `free_clean` payı düşüyor, `ads_iap` artıyor: 1,000+ bandında free_clean %64.05 / ads_iap %5.61 (n=37,498); 1,000,000+ bandında %21.13 / %35.10 (n=4,065); 10,000,000+ bandında %12.59 / %56.05 (n=1,017). `paid` %2.20'den (1,000+) %0.10'a (10M+) iniyor. 500M+ bantlar n ≤ 12.
  - Q3: Reklam oranı en yüksek türlerin 9'u oyun (Simulation %90.13, Word %89.35, Racing %88.89...); oyun dışı tek tür Personalization (%81.24, n=3,753).
  - Q6: `Individual developer` (genel etiket) hariç en büyük geliştirici WABiz domain'siz hesabı (534, %0.53). Genel etiket 6,022 (%6.02) ayrı satırda.
  - Q7: Ücretsiz oranı 2010 kohortunda %85.91, 2018 sonrası %98-99. IAP oranı 2023 %18.33 → 2025 %28.34 → 2026 %36.04. 2013 kohortu sıra dışı (reklam %65.31, IAP %43.35): GPSmyCity'nin 380 uygulaması (%100 reklam+IAP) bu kohortta; hariç tutulunca IAP %30.59. 2026 kohortu yalnızca 1 Ocak-6 Haziran.
  - Q9: Son 12 ayda güncellenmemiş oranı 1,000+ bandında %32.35 (n=37,498), 1,000,000+ %15.89 (n=4,065), 10,000,000+ %10.91 (n=1,017).
  - Q10: Finance %80.16 free_clean (tüm veri %49.38), Productivity %64.32; Entertainment'ta ads_only %47.98 (tüm veri %30.87).
- Sorun:
  - `queries.sql` yorumundaki ";" bölücüyü bozdu (Q6). Yorumlardan ";" kaldırıldı.
  - Q2/Q9'da 50M+ bantlarının n'i küçük (128, 96, 12, 6, 1, 1). Grafiklerde bu bantlar birleştirilecek (Adım 7 kararı).
- Elenen türler (n < 200, Q3 ve Q4 karşılaştırmaları): Comics (74), Libraries & Demo (127), Music (143). Q1, Q5, Q8 listeleme olduğu için tüm türleri içeriyor.
- Süre: ~45 dk
- Sonraki: Adım 7, 3-5 grafik.
### 2026-10-31 | Adım 7: Grafikler
- Yapılan: `src/figures.py` yazıldı, 4 grafik `figures/` altına kaydedildi (PNG, 150 dpi). Notebook'a Adım 7 hücresi eklendi (26 hücre, 0 hata).
  - `01_band_monetization.png`: kurulum bandı × gelir modeli, %100 yığılmış çubuk.
  - `02_genre_monetization.png`: tür × gelir modeli (n ≥ 200, 46 tür), reklamsız/IAP'siz paya göre sıralı.
  - `03_focus_genres.png`: Productivity, Finance, Entertainment ve tüm veri (Q10).
  - `04_stale_by_band.png`: son 12 ayda güncellenmemiş pay, kurulum bandına göre (Q9).
  - Her grafikte başlık, eksen adı ve birim, her çubukta n, altta "Okuma:" notu ve kaynak/örneklem notu var. Gelir modeli renkleri sabit kategorik palet (5 renk, renk körlüğü için doğrulandı); 3 açık renk düşük kontrastlı olduğundan ≥%8 segmentlere doğrudan yüzde etiketi kondu.
- Bulunan:
  - Reklamsız/IAP'siz pay en yüksek Business (%90), en düşük Simulation (%4). En düşük 20 türün 15'i oyun (n ≥ 200 olan 16 oyun türünden yalnızca Casino en düşük 20'nin dışında).
  - Personalization'da ücretli pay %13 (488 uygulama); bunların 175'i tek geliştiriciden (Samtree, saat yüzü), ilk 4 geliştirici 335 uygulama. Tür oranları büyük geliştiricilere duyarlı (Adım 4 riski).
- Sorun: İlk sürümde okuma notu x ekseni etiketiyle çakıştı ve 03'te lejant başlığa bindi. Başlık ve not eksene bağlanarak düzeltildi, PNG'ler gözle kontrol edildi.
- Varsayım: 50M ve üstü 6 kurulum bandı (128+96+12+6+1+1 = 244 uygulama) grafiklerde "50,000,000+" olarak birleştirildi. SQL Q2/Q9 sonuçları ayrık bantlarla duruyor.
- Süre: ~45 dk
- Sonraki: Adım 8, Streamlit dashboard.
### 2026-10-31 | Adım 8: Streamlit dashboard
- Yapılan: `app/dashboard.py` yazıldı (`streamlit run app/dashboard.py`). `data/apps.db`'den JOIN ile okur, `st.cache_data` ile önbellekler.
  - Üstte sabit not: "Tam verinin %9'u, geliştirici bazlı örneklem" + ABD/Haziran 2026/Android + "ilişki, neden-sonuç değil".
  - Filtreler tek satırda: tür (çoklu seçim), tip (Tümü/Oyun/Uygulama = `is_game`), kurulum bandı (çoklu seçim). Seçimdeki n her zaman görünür.
  - 3 sekme: Tür × gelir modeli (n < 200 türler gizlenir ve adları yazılır), Kurulum bandı × gelir modeli, Geliştirici yoğunlaşması (en büyük 10, `Individual developer` sıralama dışı ayrı metrik, ilk 10'un gelir modeli tablosu).
  - Her grafikte eksen adı/birim, çubuk etiketinde n, üzerine gelince ipucu (pay, n), altında "Okuma:" notu. Renkler `figures/` ile aynı.
  - `.streamlit/config.toml`: sunucu yalnızca `localhost`'a bağlanır, kullanım istatistiği kapalı. Varsayılan ayarda Streamlit yerel ağ ve dış IP adresini de yayınlıyordu.
- Bulunan (test): `streamlit.testing.AppTest` ile açılış ve 3 filtre senaryosu hatasız (exception 0). Varsayılan görünüm: n = 100,013, 46 tür, gizlenen türler Comics, Libraries & Demo, Music; 47,956 geliştirici, ilk 10 (genel etiket hariç) %3.33, genel etiket 6,022. "Oyun" filtresi n = 14,728. Comics tek başına seçilince n = 0 ve boş durum mesajı gösteriliyor. Finance + 1,000,000+ n = 200. Sunucu `localhost:8599`'da başladı, sağlık kontrolü HTTP 200.
- Sorun: `use_container_width` Streamlit 1.66'da kullanımdan kalkmış, `width="stretch"` ile değiştirildi. Dashboard tarayıcıda gözle kontrol edilmedi (bu oturumda ekran görüntüsü alınmadı); İbrahim'in bir kez açıp bakması gerekiyor.
- Herkese açık yayın yapılmadı. Yayın için ham satır yerine özet tablolar kullanılmalı: bu karar İbrahim'de (TASK kuralı 9).
- Süre: ~40 dk
- Sonraki: Adım 9, 3 bulgu + sınırlamalar + ürün çıkarımı, README.
### 2026-10-31 | Adım 9: Bulgular, sınırlamalar, ürün çıkarımı, README
- Yapılan: README.md dolduruldu (özet, 3 bulgu + her birine sınırlama, genel sınırlamalar, ürün çıkarımı tablosu, lisans, yöntem, yeniden üretim). DEVLOG'daki Bulgular, Ürün çıkarımı, Ne öğrendim, Sonraki adımlar ve LinkedIn bölümleri dolduruldu. Tüm sayılar Q2, Q9, Q10 ve `figures.py` sorgularının çıktısından.
- Bulunan: 3 bulgu kurulum bandı × gelir modeli, tür × gelir modeli ve güncelleme tazeliği × kurulum bandı. Ürün çıkarımı "doğrudan bağ yok". Uygulama tanımları İbrahim'in diğer proje dosyalarından alındı: `profile-readme/README.md` (PomoQuest, SpendWise) ve `Flutter Projects/if22-watchlist/DEVLOG.md` (Pairplot).
- Sorun: README taslağında iki ifade koddan doğrulanmamıştı ("Finance uygulamalarının çoğu muhtemelen banka uygulaması" ve "klavye hesaplarının 1,053 uygulamasının hepsi yalnızca reklam"). İlki çıkarıldı, ikincisi "~%99" olarak düzeltildi. README lisans satırı BY-NC-SA olarak güncellendi.
- Süre: ~40 dk
- Sonraki: Adım 10, kalite kontrol listesi.
### 2026-10-31 | Adım 10: Kalite kontrol
- Yapılan: `05-kalite-kontrol.md` yazıldı. Üretilmiş dosyalar (`apps_clean.csv`, `apps.db`, `figures/*.png`) silinip notebook `nbconvert --execute` ile sıfırdan çalıştırıldı. README/DEVLOG'daki 14 ana sayı notebook çıktısında arandı. README ve DEVLOG'da nedensel dil tarandı. Kullanılmayan `.gitkeep` dosyaları silindi.
- Bulunan: 19/19 kod hücresi sırayla çalıştı, 0 hata, 0 stderr. Tüm üretilmiş dosyalar ve 4 grafik yeniden oluştu. 14 sayının 14'ü notebook çıktısında birebir var. Nedensel ifade bulunmadı.
- Sorun: Dashboard tarayıcıda gözle kontrol edilmedi (yalnızca AppTest ve sağlık kontrolü).
- Açık kararlar (İbrahim): `git init` ve repo; notebook çıktılarının (~976 KB) repoda tutulması; dashboard'un herkese açık yayını; Kaggle lisans kutusunun gözle teyidi.
- Süre: ~20 dk
- Sonraki: İbrahim'in açık kararları. Kapsam dışı kalanlar "Sonraki adımlar"da.

## Veri kalite notları
- Satır/sütun: 100,013 x 19, dosya 20,016,745 bayt (Adım 2, `src/validate.py`)
- Tipler: `is_game`, `free`, `contains_ads`, `offers_iap` bool olarak okunuyor. `score/ratings/reviews/price` float (eksik değer yüzünden `ratings/reviews` int değil). `released`, `last_updated` str, hepsi `YYYY-MM-DD` olarak sorunsuz parse ediliyor.
- Eksik değerler: `score/ratings/reviews` 68,258 (%68.25, üçü birlikte boş), `developer_domain` 36,486 (%36.48), `released` 17,467 (%17.46), `price` 13 (%0.01), `fliar_profile_url` 69,638 (%69.63, analizde kullanılmıyor). Diğerleri 0.
- Tekrarlı satırlar: tam tekrar 0, tekrarlı `app_id` 0.
- Aykırı değerler:
  - `score` 1.00-5.00 aralığında, dışı 0. `reviews > ratings` 0, negatif sayı 0.
  - `free=True` ve `price > 0` 0. `free=False` ve `price` boş 13.
  - Fiyat (ücretli, n=1,463): medyan 1.99, %90 7.99, %99 29.99, max 294.99 USD (SamWatch saat yüzü, Personalization). Yüksek fiyatlar gerçek ürün gibi görünüyor, aykırı diye silinmiyor.
  - `released` 2010-01-28 → 2026-06-06, `last_updated` 2009-07-19 → 2026-06-08. Tarama tarihinden (2026-06-08) sonra güncelleme 0. `last_updated < released` 199.
- Silinen/değiştirilen: silinen satır 0. Değiştirilen: 351 satırın `genre` değeri "Sports" → "Sports (Game)". Atılan sütun: `fliar_profile_url`.
- Örneklem sağlaması (kıyas: reklam %43, IAP %18, ücretli %1.4, tam veri): örneklem reklam %43.44, IAP %18.50, ücretli %1.48; sapma +0.44 / +0.50 / +0.08 puan. En büyük 10 geliştirici %9.10 (`Individual developer` hariç %3.33). Düzeltme yapılmadı.

## Bulgular (analiz bittikten sonra doldurulur)
| # | Bulgu | Kanıt (sayı/grafik) | Sınırlama |
|---|-------|---------------------|-----------|
| 1 | Kurulum bandı büyüdükçe reklam + IAP birlikte kullanan uygulamaların payı artıyor, reklamsız/IAP'siz olanların payı düşüyor | Q2: 1,000+ bandında free_clean %64.05 / ads_iap %5.61 (n=37,498); 10,000,000+ bandında %12.59 / %56.05 (n=1,017). `figures/01_band_monetization.png` | Bantlar geniş alt sınırlar; büyük uygulamalar yaş ve geliştirici açısından da farklı. İlişki, neden-sonuç değil |
| 2 | Oyun türlerinde reklamsız/IAP'siz uygulama nadir, Business ve Finance'ta çoğunluk | Reklamsız/IAP'siz pay Business %90.38 (n=5,989), Simulation %4.45 (n=1,662); en düşük 20 türün 15'i oyun. `figures/02_genre_monetization.png` | Tür oranları tek modelli büyük geliştiricilere duyarlı (klavye/tema hesapları 1,053 uygulama, Samtree 175 ücretli Personalization). n < 200 olan 3 tür dışarıda |
| 3 | Küçük kurulum bantlarında son 12 ayda güncellenmemiş uygulama payı daha yüksek | Q9: 1,000+ %32.35 (n=37,498), 1,000,000+ %15.89 (n=4,065), 10,000,000+ %10.91 (n=1,017). `figures/04_stale_by_band.png` | `last_updated` tek tarih, güncellemenin içeriğini göstermez; 365 gün eşiği bir seçim |

## Ürün çıkarımı
**Doğrudan bağ yok.** Veri bir türde hangi gelir modelinin yaygın olduğunu gösteriyor; hangisinin daha çok kazandırdığını ya da kullanıcı tuttuğunu göstermiyor. PomoQuest ve SpendWise yalnızca iOS'ta, bu veri Android (platform farkı sınırlaması).
- SpendWise (fatura/abonelik takibi, iOS) → Finance: %80.16 reklamsız/IAP'siz (tüm veri %49.38). Bunların ne kadarının bağımsız takipçi, ne kadarının banka/hizmet uygulaması olduğu veride yok; zayıf bağlam.
- PomoQuest (oyunlaştırılmış Pomodoro, iOS) → Productivity: yalnızca IAP %7.61, tüm veriden (%5.79) biraz yüksek. Oyun benzeri tasarım onu reklam ağırlıklı oyun türlerine taşımıyor.
- Pairplot (çiftler için izleme listesi, Flutter iOS + Android) → Entertainment: üç tür içinde en reklam ağırlıklısı (yalnızca reklam %47.98). Reklamsız kalmak türün çoğundan ayırır; bunun işe yarayıp yaramadığını veri söyleyemez.

## Ne öğrendim
- Teknik: SQLite'ta `AVG(koşul)` ile oran hesaplamak CASE pivotlarından kısa. Pencere fonksiyonları (`SUM OVER`, `ROW_NUMBER`) kümülatif pay ve tür içi sıralamayı tek sorguda veriyor. `.sql` dosyasını yorum işaretlerine göre bölerken yorum içindeki `;` sorguyu kırdı.
- Yöntem: Genel oranlar tam veriyle 1 puandan az farkla tutsa da tür düzeyinde birkaç büyük geliştirici oranı kaydırabiliyor (Personalization, 2013 kohortu/GPSmyCity). Örneklem sağlaması tek bir genel oranla bitmemeli.
- Yapmasaydım iyi olurdu dediğim: Bulgu cümlesini grafikten gözle okuyup yazdım ("en düşük 20 türün 14'ü oyun"), kodla kontrol edince 15 çıktı. Her sayıyı yazmadan önce sorguyla doğrulamak gerekiyor.

## Sonraki adımlar (kapsam dışı kalanlar)
- Tür düzeyi oranları büyük geliştiricileri (klavye/tema hesapları, GPSmyCity) hariç tutarak yeniden hesaplamak (duyarlılık analizi).
- (developer, domain) anahtarının aynı şirketi bölmesi (WABiz) için isim normalizasyonu.
- Yedek soru 1 (reklamlı ve reklamsız ücretsiz uygulamaların puanı): puan yalnızca %31.75'te var ve ücretli tarafa kayık; ana soru dışında kaldı.
- Dashboard'u herkese açık yayınlamak: özet tablolara geçiş ve yayın kararı İbrahim'de.

## LinkedIn için ham notlar
- Açılış cümlesi (bulgu ile başla): Google Play'de 1,000+ kurulumlu uygulamaların yalnızca %5.6'sı reklam ve uygulama içi satın almayı birlikte kullanıyor; 10M+ kurulumda bu oran %56.
- Öne çıkan grafik: `figures/01_band_monetization.png` (kurulum bandı × gelir modeli). Yedek: `02_genre_monetization.png` (oyunlar vs Business/Finance).
- Tek cümlelik ders: Örneklem genel oranlarda tam veriyle uyuşsa bile, tek tip çalışan birkaç büyük geliştirici tür düzeyindeki tabloyu değiştirebilir.
- Notlar: 100,013 uygulama, %9 geliştirici bazlı örneklem, ABD/Haziran 2026, Android. Araçlar: pandas, SQLite (10 soru), Streamlit. Lisans CC BY-NC-SA 4.0, ticari kullanım yok, kaynak atfı şart. "Reklam büyümeyi sağlıyor" gibi nedensel cümle kurma.
