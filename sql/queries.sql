-- Google Play Apps 2026 örneklemi: 10 SQL sorusu.
-- Her blok "-- Q<n>: <soru>" satırıyla başlar ve ";" ile biter; notebook bu işaretlere göre böler.
-- Minimum örnek kuralı: tür karşılaştırmalarında n < 200 olan türler elenir
-- (Comics 74, Libraries & Demo 127, Music 143).

-- Q1: Tür başına uygulama sayısı ve toplam içindeki payı nedir?
SELECT
    genre,
    g.is_game,
    COUNT(*) AS n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM apps
JOIN genres AS g USING (genre)
GROUP BY genre, g.is_game
ORDER BY n DESC;

-- Q2: Kurulum bandına göre gelir modeli dağılımı nasıl değişiyor?
SELECT
    b.band_rank,
    a.installs,
    COUNT(*) AS n,
    ROUND(100.0 * SUM(CASE WHEN a.monetization = 'free_clean' THEN 1 ELSE 0 END) / COUNT(*), 2) AS free_clean_pct,
    ROUND(100.0 * SUM(CASE WHEN a.monetization = 'ads_only' THEN 1 ELSE 0 END) / COUNT(*), 2) AS ads_only_pct,
    ROUND(100.0 * SUM(CASE WHEN a.monetization = 'ads_iap' THEN 1 ELSE 0 END) / COUNT(*), 2) AS ads_iap_pct,
    ROUND(100.0 * SUM(CASE WHEN a.monetization = 'iap_only' THEN 1 ELSE 0 END) / COUNT(*), 2) AS iap_only_pct,
    ROUND(100.0 * SUM(CASE WHEN a.monetization = 'paid' THEN 1 ELSE 0 END) / COUNT(*), 2) AS paid_pct
FROM apps AS a
JOIN install_bands AS b USING (installs)
GROUP BY b.band_rank, a.installs
ORDER BY b.band_rank;

-- Q3: Reklam oranı en yüksek 10 tür hangisi (n >= 200)?
SELECT
    genre,
    COUNT(*) AS n,
    ROUND(100.0 * AVG(contains_ads), 2) AS ads_pct,
    ROUND(100.0 * AVG(offers_iap), 2) AS iap_pct
FROM apps
GROUP BY genre
HAVING COUNT(*) >= 200
ORDER BY ads_pct DESC
LIMIT 10;

-- Q4: Her tür içinde uygulamalar puana göre nasıl sıralanıyor (ratings >= 1000, n >= 200 tür)?
WITH eligible AS (
    SELECT genre FROM apps GROUP BY genre HAVING COUNT(*) >= 200
)
SELECT
    a.genre,
    a.title,
    a.score,
    a.ratings,
    a.monetization,
    RANK() OVER (PARTITION BY a.genre ORDER BY a.score DESC) AS score_rank,
    COUNT(*) OVER (PARTITION BY a.genre) AS n_in_genre
FROM apps AS a
JOIN eligible USING (genre)
WHERE a.ratings >= 1000
ORDER BY a.genre, score_rank;

-- Q5: Her türün en yüksek puanlı 3 uygulaması hangisi (ratings >= 1000, eşitlikte çok oy alan önde)?
WITH ranked AS (
    SELECT
        genre,
        title,
        score,
        ratings,
        monetization,
        ROW_NUMBER() OVER (PARTITION BY genre ORDER BY score DESC, ratings DESC) AS rn
    FROM apps
    WHERE ratings >= 1000
)
SELECT genre, rn, title, score, ratings, monetization
FROM ranked
WHERE rn <= 3
ORDER BY genre, rn;

-- Q6: En çok uygulaması olan 10 geliştirici kim ve toplam içindeki payı ne?
-- "Individual developer" + boş domain genel bir etiket. Sıralama dışı, ayrı satırda raporlanır.
WITH dev_counts AS (
    SELECT
        d.developer_id,
        d.developer,
        d.developer_domain,
        (d.developer = 'Individual developer' AND d.developer_domain IS NULL) AS is_generic,
        COUNT(*) AS n_apps
    FROM apps AS a
    JOIN developers AS d USING (developer_id)
    GROUP BY d.developer_id
),
top10 AS (
    SELECT * FROM dev_counts WHERE NOT is_generic ORDER BY n_apps DESC LIMIT 10
),
report AS (
    SELECT developer, developer_domain, is_generic, n_apps FROM top10
    UNION ALL
    SELECT developer, developer_domain, is_generic, n_apps FROM dev_counts WHERE is_generic
)
SELECT
    developer,
    developer_domain,
    is_generic,
    n_apps,
    ROUND(100.0 * n_apps / (SELECT COUNT(*) FROM apps), 2) AS pct
FROM report
ORDER BY is_generic, n_apps DESC;

-- Q7: Yayın yılı kohortuna göre ücretsiz / reklam / IAP oranı nasıl değişiyor?
SELECT
    release_year,
    COUNT(*) AS n,
    ROUND(100.0 * AVG(free), 2) AS free_pct,
    ROUND(100.0 * AVG(contains_ads), 2) AS ads_pct,
    ROUND(100.0 * AVG(offers_iap), 2) AS iap_pct
FROM apps
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year;

-- Q8: Türler büyükten küçüğe dizildiğinde kümülatif pay nedir, ilk 10 tür uygulamaların % kaçı?
WITH genre_counts AS (
    SELECT genre, COUNT(*) AS n FROM apps GROUP BY genre
)
SELECT
    ROW_NUMBER() OVER (ORDER BY n DESC) AS genre_rank,
    genre,
    n,
    ROUND(100.0 * n / SUM(n) OVER (), 2) AS pct,
    ROUND(100.0 * SUM(n) OVER (ORDER BY n DESC ROWS UNBOUNDED PRECEDING) / SUM(n) OVER (), 2) AS cumulative_pct
FROM genre_counts
ORDER BY genre_rank;

-- Q9: Son 12 ayda (tarama tarihi 2026-06-08'e göre > 365 gün) güncellenmemiş uygulama oranı kurulum bandına göre nasıl?
SELECT
    b.band_rank,
    a.installs,
    COUNT(*) AS n,
    SUM(a.days_since_update > 365) AS n_stale,
    ROUND(100.0 * AVG(a.days_since_update > 365), 2) AS stale_pct,
    CAST(AVG(a.days_since_update) AS INTEGER) AS mean_days_since_update
FROM apps AS a
JOIN install_bands AS b USING (installs)
GROUP BY b.band_rank, a.installs
ORDER BY b.band_rank;

-- Q10: Productivity, Finance ve Entertainment türlerinin gelir modeli profili tüm veriyle nasıl kıyaslanıyor?
WITH scoped AS (
    SELECT genre AS segment, monetization FROM apps
    WHERE genre IN ('Productivity', 'Finance', 'Entertainment')
    UNION ALL
    SELECT 'ALL', monetization FROM apps
),
profile AS (
    SELECT
        segment,
        COUNT(*) AS n,
        ROUND(100.0 * AVG(monetization = 'free_clean'), 2) AS free_clean_pct,
        ROUND(100.0 * AVG(monetization = 'ads_only'), 2) AS ads_only_pct,
        ROUND(100.0 * AVG(monetization = 'ads_iap'), 2) AS ads_iap_pct,
        ROUND(100.0 * AVG(monetization = 'iap_only'), 2) AS iap_only_pct,
        ROUND(100.0 * AVG(monetization = 'paid'), 2) AS paid_pct
    FROM scoped
    GROUP BY segment
)
SELECT * FROM profile
ORDER BY segment = 'ALL', segment;
