# TASK: Google Play Apps 2026 | Gelir Modeli, Tür ve Kurulum Bandı

## Bağlam
- Kaggle linki: https://www.kaggle.com/datasets/fliarbi/google-play-apps-2026
- Dosya: `google_play_apps_2026_sample.csv`
- Lisans: ÇELİŞKİLİ (Adım 2). REPORT.md "CC BY-NC 4.0" diyor, Kaggle API (`kaggle datasets download` çıktısı) "CC-BY-NC-SA-4.0" diyor. Daha sıkı olan (BY-NC-SA: ticari kullanım yok, atıf zorunlu, türev aynı lisansla paylaşılır) esas alınır. Ticari kullanım yok, atıf zorunlu.
- Seviye: 2 (SQL + dashboard)
- Süre bütçesi: 2 hafta, haftada 4-5 saat

## Ana soru
Google Play'de gelir modeli (reklam, uygulama içi satın alma, ücretli, hiçbiri) tür ve kurulum bandına göre nasıl değişiyor?

Yedek sorular:
1. Ücretsiz uygulamalarda reklamlı olanların puanı reklamsızlardan farklı mı?
2. Güncelleme tazeliği kurulum bandıyla nasıl değişiyor?

## Veri bilgisi
- Satır/sütun: 100,013 satır, 19 sütun (dosya özetinden doğrulandı). Dosya boyutu 20,016,745 bayt (~20.0 MB), Adım 2'de doğrulandı.
- Örneklem yapısı: tam verinin %9'u (1,101,050 uygulama). Geliştirici bazlı hash örneklemi: seçilen geliştiricilerin tüm uygulamaları dahil. Rastgele uygulama örneği DEĞİL.
- Sütunlar (data card ve dosya özetiyle doğrulandı):
  `app_id` (str), `title` (str), `developer` (str), `developer_domain` (str), `genre` (str), `is_game` (bool), `installs` (str, kurulum bandı, örn. "1,000,000+"), `score` (float), `ratings` (int), `reviews` (int), `free` (bool), `price` (float), `currency` (str), `contains_ads` (bool), `offers_iap` (bool), `content_rating` (str), `released` (date), `last_updated` (date), `fliar_profile_url` (str)
- Eksik değerler (Adım 2'de ölçüldü): `score/ratings/reviews` %68.25 (68,258), `developer_domain` %36.48 (36,486), `released` %17.46 (17,467), `price` %0.01 (13, hepsi `free=False`), `fliar_profile_url` %69.63 (kullanılmıyor). Diğer sütunlarda eksik yok. Data card'a göre `score/ratings/reviews` puan gösterilmeyen uygulamalarda, `released` tarih gizliyse, `developer_domain` site yoksa veya sosyal/hosting sayfasıysa boş. Gerçek oranlar Adım 2'de ölçülür.
- Sağlama için kıyas değerleri (TAM veri, REPORT.md): reklam gösteren %43, IAP satan %18, ücretli %1.4. Bunlar bulgu değil, yalnızca örneklem sağlamasıdır.
- Bilinen riskler:
  1. Geliştirici bazlı örneklem: büyük geliştiriciler (yüzlerce uygulamalı hesaplar) oranları kaydırabilir.
  2. `installs` tam sayı değil geniş bant (örn. 1,000,000+ aslında 1M-5M).
  3. Puan yalnızca uygulamaların yaklaşık üçte birinde var (REPORT.md'ye göre). Puan analizleri bu alt kümeyle sınırlı.
  4. Veri ABD mağazasından, Haziran 2026 anlık görüntüsü (tarama 7-8 Haziran 2026).
  5. `genre` değerleri örtüşüyor ("Music" / "Music & Audio", "Education" / "Educational"). Birleştirme kararı loglanır.
  6. "Individual developer" gibi genel adlar farklı kişileri birleştirir.
  7. Android verisi: iOS uygulamalarına doğrudan yansıtılamaz.

## Kurallar
1. Önce `DEVLOG.md` ve bu dosyayı oku. Her adımın sonunda `DEVLOG.md`'ye kayıt ekle.
2. İlk adım veriyi doğrulamak: indir (`kaggle datasets download -d fliarbi/google-play-apps-2026 -p data/ --unzip`), şekli, sütun tiplerini, eksik değerleri, tekrarlı satırları raporla. Bu rapor bu dosyadaki "DOĞRULANMADI" ifadelerini düzeltir.
3. Veri `data/` altında kalır ve git'e girmez (`.gitignore`).
4. Sonuç uydurma. Her sayı kodun çıktısından gelsin. Çalıştırmadığın analizi bulgu diye yazma.
5. Her grafik: başlık, eksen adı, birim, tek cümle okuma notu. Her grafikte n (gözlem sayısı) görünsün.
6. Her bulgunun yanına bir sınırlama yaz.
7. Varsayım yaptıysan `DEVLOG.md`'de "Varsayımlar" altına yaz.
8. Kapsamı büyütme. Ana soru dışında bir şeye 30 dakikadan fazla harcama, "Sonraki adımlar"a not düş. Seviye 2'de ML ekleme.
9. Büyük bir karar gerekiyorsa (veri silme, soruyu değiştirme, dashboard'u herkese açık yayınlama) dur ve İbrahim'e sor.
10. Yalnızca verilen CSV kullanılır. Radar API'ye, `fliar_profile_url` linklerine veya başka bir kaynağa gidilmez.
11. REPORT.md'deki sayılar bulgu olarak yazılmaz. Sadece örneklem sağlaması için kıyas amaçlı kullanılır ve sapma DEVLOG'a yazılır.
12. "Nedensel" dil yok: "reklam puanı düşürüyor" değil, "reklamlı uygulamaların puanı daha düşük" denir.

## Adımlar
1. [x] Repo iskeleti: `data/`, `notebooks/`, `figures/`, `src/`, `sql/`, `app/`, `requirements.txt` (sürümler sabit), `.gitignore` (`data/` dahil)
2. [x] Veriyi indir ve doğrula (şekil, tipler, eksik, tekrar, aykırı fiyat/puan)
3. [x] Temizleme ve türetilmiş sütunlar (aşağıda), her karar loglanır
4. [x] Örneklem sağlaması: reklam/IAP/ücretli oranlarını kıyas değerleriyle karşılaştır, geliştirici bazlı yoğunlaşmayı ölç (en büyük 10 geliştiricinin payı). Sapmayı DEVLOG'a yaz, "düzeltme" yapma.
5. [x] SQLite şeması ve yükleme (Seviye 2 bölümü)
6. [x] SQL soruları (10 adet) `sql/queries.sql`, sonuçlar notebook'tan çalıştırılır
7. [x] En iyi 3-5 grafiği `figures/` altına kaydet
8. [x] Streamlit dashboard (`app/dashboard.py`), yerelde çalışır
9. [x] 3 bulgu + sınırlamalar + ürün çıkarımı, README'yi doldur
10. [x] Kontrol listesi (`05-kalite-kontrol.md`): notebook baştan sona temiz çalışıyor mu?

## Seviye 2: SQL ve dashboard

**Türetilmiş sütunlar (Adım 3)**
- `installs_min`: `installs` bandından tamsayı (örn. "1,000,000+" -> 1000000)
- `monetization`: `free = False` ise `paid`; değilse `ads_iap`, `ads_only`, `iap_only`, `free_clean`. Ücretli uygulamada reklam/IAP de olabilir, ücretli olan tek kategoriye `paid` yazılır. Bu bir varsayımdır, DEVLOG'a yaz.
- `is_rated`: `score` boş değil
- `release_year`: `released` yılı
- `days_since_update`: referans tarih sabit 2026-06-08 (tarama tarihi), bugünün tarihi KULLANILMAZ

**Şema (Adım 5, `sql/schema.sql`)**
- `apps` (app_id PK, title, developer_id FK, genre FK, installs FK, score, ratings, reviews, free, price, currency, contains_ads, offers_iap, content_rating, released, last_updated, monetization, is_rated, release_year, days_since_update)
- `developers` (developer_id PK, developer, developer_domain). developer_id = (developer, developer_domain) çifti. "Individual developer" + boş domain birleşimi güvenilmez, geliştirici sorgularında ayrı raporla veya dışla.
- `genres` (genre PK, is_game)
- `install_bands` (installs PK, band_rank, installs_min)

**SQL soruları (`sql/queries.sql`, her biri bir yorum satırı soru + sorgu)**
1. Tür başına uygulama sayısı ve payı (GROUP BY)
2. Kurulum bandı başına gelir modeli dağılımı (JOIN `install_bands`, CASE)
3. Reklam oranı en yüksek 10 tür (HAVING n >= 200)
4. Tür içinde puana göre sıralama (RANK window, `ratings >= 1000`)
5. Her türün en yüksek puanlı 3 uygulaması (ROW_NUMBER, PARTITION BY genre)
6. En çok uygulamalı 10 geliştirici ve toplam içindeki payı (JOIN `developers`)
7. Yayın yılına göre ücretsiz/reklam/IAP oranı (kohort)
8. Türlere göre kümülatif uygulama payı (SUM OVER): ilk 10 tür uygulamaların % kaçı?
9. Son 12 ayda güncellenmemiş uygulama oranı, kurulum bandına göre
10. Productivity, Finance ve Entertainment türlerinin gelir modeli profili vs tüm veri (CTE)

Minimum örnek kuralı: karşılaştırmalarda n < 200 olan türler elenir ve elenenler DEVLOG'a yazılır.

**Dashboard (Adım 8, Streamlit)**
- Sayfa üstünde sabit not: "Tam verinin %9'u, geliştirici bazlı örneklem"
- 3 sekme: Tür × gelir modeli, Kurulum bandı × gelir modeli, Geliştirici yoğunlaşması
- Filtreler: tür, `is_game`, kurulum bandı
- Her grafikte n gösterilir
- Önce yerelde çalışır. Herkese açık yayınlamak için ham satır yerine yalnızca özet tablolar kullanılır. Bu karar için İbrahim'e sor.

## Ürün çıkarımı
Productivity, Finance ve Entertainment türlerinin gelir modeli profilini PomoQuest, SpendWise ve Pairplot ile karşılaştır. Veri doğal bir bağı desteklemiyorsa "doğrudan bağ yok" yaz. Platform farkını (Android vs iOS) mutlaka sınırlama olarak ekle.

## Teslim
- Çalışır notebook, `sql/schema.sql`, `sql/queries.sql`, `app/dashboard.py`, `figures/`, doldurulmuş `README.md` ve `DEVLOG.md`
- Çıktının sonunda: 3 bulgu, 3 sınırlama, 1 ürün çıkarımı, LinkedIn taslağı için ham notlar
