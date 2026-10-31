-- Google Play Apps 2026 örneklemi, normalize SQLite şeması.
-- Boolean sütunlar INTEGER 0/1, tarihler TEXT (YYYY-MM-DD).

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS apps;
DROP TABLE IF EXISTS developers;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS install_bands;

-- Geliştirici kimliği = (developer, developer_domain) çifti.
-- "Individual developer" + boş domain birçok farklı kişiyi birleştirir; sorgularda ayrı raporlanır veya dışlanır.
CREATE TABLE developers (
    developer_id     INTEGER PRIMARY KEY,
    developer        TEXT NOT NULL,
    developer_domain TEXT,
    UNIQUE (developer, developer_domain)
);

-- "Sports" oyunları "Sports (Game)" olarak ayrıldı, böylece her türün tek is_game değeri var.
CREATE TABLE genres (
    genre   TEXT PRIMARY KEY,
    is_game INTEGER NOT NULL CHECK (is_game IN (0, 1))
);

-- installs_min bandın alt sınırı: "1,000,000+" gerçekte 1M-5M aralığı.
CREATE TABLE install_bands (
    installs     TEXT PRIMARY KEY,
    band_rank    INTEGER NOT NULL UNIQUE,
    installs_min INTEGER NOT NULL UNIQUE
);

CREATE TABLE apps (
    app_id            TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    developer_id      INTEGER NOT NULL REFERENCES developers (developer_id),
    genre             TEXT NOT NULL REFERENCES genres (genre),
    installs          TEXT NOT NULL REFERENCES install_bands (installs),
    score             REAL CHECK (score BETWEEN 1 AND 5),
    ratings           INTEGER,
    reviews           INTEGER,
    free              INTEGER NOT NULL CHECK (free IN (0, 1)),
    price             REAL,
    currency          TEXT,
    contains_ads      INTEGER NOT NULL CHECK (contains_ads IN (0, 1)),
    offers_iap        INTEGER NOT NULL CHECK (offers_iap IN (0, 1)),
    content_rating    TEXT,
    released          TEXT,
    last_updated      TEXT NOT NULL,
    monetization      TEXT NOT NULL CHECK (monetization IN ('paid', 'ads_iap', 'ads_only', 'iap_only', 'free_clean')),
    is_rated          INTEGER NOT NULL CHECK (is_rated IN (0, 1)),
    release_year      INTEGER,
    days_since_update INTEGER NOT NULL
);

CREATE INDEX idx_apps_genre ON apps (genre);
CREATE INDEX idx_apps_installs ON apps (installs);
CREATE INDEX idx_apps_developer ON apps (developer_id);
CREATE INDEX idx_apps_monetization ON apps (monetization);
