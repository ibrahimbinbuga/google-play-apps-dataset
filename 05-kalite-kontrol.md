# Kalite kontrol (2026-10-31)

Temiz çalıştırma: `data/` altındaki üretilmiş dosyalar (`apps_clean.csv`, `apps.db`) ve `figures/*.png` silindi, ham CSV tutuldu, sonra `jupyter nbconvert --to notebook --execute --inplace notebooks/analysis.ipynb` çalıştırıldı.

## Notebook
- [x] Baştan sona hatasız çalışıyor: 19 kod hücresinin 19'u çalıştı, 0 hata, 0 stderr çıktısı
- [x] Çalışma sırası sıralı (1..19), elle çalıştırılmış eski hücre yok
- [x] `apps_clean.csv` ve `apps.db` yeniden üretildi (100,013 satır, FK hatası 0)
- [x] 4 grafik `figures/` altında yeniden üretildi
- [x] Mantık `src/` modüllerinde (`validate`, `clean`, `sample_check`, `load_db`, `queries`, `figures`); notebook sadece fonksiyonları çağırıyor
- [x] README ve DEVLOG'daki 14 ana sayı (Q2, Q9, Q10, örneklem sağlaması) notebook çıktısında birebir bulunuyor

## Veri ve temizleme
- [x] Silinen satır 0. Tek değişiklik: 351 Sports oyunu `Sports (Game)` (İbrahim onayladı)
- [x] Doldurma (imputation) yok; `price` boş 13 satır ve puansız 68,258 satır olduğu gibi
- [x] `days_since_update` sabit referans tarihten (2026-06-08), bugünün tarihi kullanılmadı
- [x] Örneklem sağlaması yapıldı, düzeltme/ağırlıklandırma yok (sapma ≤ 0.5 puan)
- [x] Yalnızca verilen CSV kullanıldı; `fliar_profile_url` atıldı, dış kaynağa gidilmedi

## SQL
- [x] `sql/schema.sql`: 4 tablo, PK/FK/CHECK, `PRAGMA foreign_key_check` hatası 0
- [x] `sql/queries.sql`: 10 soru, her biri yorum satırı soru + sorgu; notebook'tan çalışıyor
- [x] Minimum örnek kuralı: n < 200 türler (Comics, Libraries & Demo, Music) karşılaştırmalarda elendi ve DEVLOG'a yazıldı
- [x] `Individual developer` genel etiketi geliştirici sıralamasında ayrı raporlandı

## Grafikler (kural 5)
- [x] 4 grafiğin hepsinde başlık, eksen adı ve birim var
- [x] Her çubukta n görünüyor; altta tek cümlelik okuma notu ve örneklem notu var
- [x] Okuma notundaki sayılar koddan geliyor (f-string), elle yazılmadı
- [x] Renk paleti renk körlüğü için doğrulandı; düşük kontrastlı renkler için segmentlerde doğrudan yüzde etiketi var
- [x] Görsel kontrol yapıldı: etiket çakışması düzeltildi (01, 03, 04 okuma notu; 03 lejant/başlık)

## Dashboard
- [x] `streamlit run app/dashboard.py` yerelde çalışıyor (AppTest: 4 senaryo, exception 0; sağlık kontrolü HTTP 200)
- [x] Üstte sabit örneklem notu, 3 sekme, 3 filtre, her grafikte n
- [x] Sunucu yalnızca `localhost`'a bağlı (`.streamlit/config.toml`), herkese açık yayın yok
- [ ] Tarayıcıda gözle kontrol: İbrahim'in bir kez açıp bakması gerekiyor

## Bulgu dili (kural 6, 11, 12)
- [x] 3 bulgunun her birinin yanında bulguya özel bir sınırlama var
- [x] Nedensel dil yok ("payı daha yüksek / artıyor", "ilişki, neden-sonuç değil")
- [x] REPORT.md sayıları bulgu olarak yazılmadı, yalnızca örneklem sağlamasında kullanıldı
- [x] Ürün çıkarımı "doğrudan bağ yok"; Android/iOS platform farkı sınırlama olarak yazıldı
- [x] ML yok; yalnızca tanımlayıcı oranlar

## Açık kalanlar
- [x] Repo: https://github.com/ibrahimbinbuga/google-play-apps-dataset (herkese açık, İbrahim onayladı, 2026-10-31)
- [x] Notebook çıktıları (~976 KB, gömülü grafikler) repoda tutuldu; GitHub'da çalıştırmadan okunabilsin diye (ai-usage-data ile aynı karar)
- [ ] Dashboard'u herkese açık yayınlama (özet tablolara geçiş gerekir), İbrahim'in kararı
- [ ] Lisans çelişkisi (Kaggle BY-NC-SA vs REPORT.md BY-NC): Kaggle sayfasındaki lisans kutusuna gözle bakılmalı
