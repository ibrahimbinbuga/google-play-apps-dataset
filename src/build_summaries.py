"""Yayın için özet tablo: dashboard ham satır yerine bunu okur (app/summary/, repoda).

Grain: geliştirici × tür × kurulum bandı × gelir modeli → uygulama sayısı (n).
Uygulama adı ve app_id yok. Geliştirici adı yalnızca örneklemde >= NAMED_MIN_APPS
uygulaması olanlarda görünür; diğerleri numarayla anonim.
"""
import sqlite3
from pathlib import Path

import pandas as pd

from load_db import DB

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "app" / "summary" / "developer_cells.csv.gz"

NAMED_MIN_APPS = 20
GENERIC_DEVELOPER = "Individual developer"

SQL = """
SELECT
    d.developer_id,
    d.developer,
    d.developer_domain,
    a.genre,
    g.is_game,
    a.installs,
    b.band_rank,
    a.monetization,
    COUNT(*) AS n
FROM apps AS a
JOIN developers AS d USING (developer_id)
JOIN genres AS g USING (genre)
JOIN install_bands AS b USING (installs)
GROUP BY d.developer_id, a.genre, a.installs, a.monetization
"""


def build(db_path: Path = DB) -> pd.DataFrame:
    with sqlite3.connect(db_path) as con:
        t = pd.read_sql_query(SQL, con)

    total = t.groupby("developer_id")["n"].transform("sum")
    t["is_generic"] = ((t["developer"] == GENERIC_DEVELOPER) & t["developer_domain"].isna()).astype(int)
    t["named"] = ((total >= NAMED_MIN_APPS) | (t["is_generic"] == 1)).astype(int)

    # Anonim numara: veritabanı id'si yerine büyüklük sırasına göre yeniden numaralanır.
    order = t.groupby("developer_id")["n"].sum().sort_values(ascending=False, kind="stable")
    dev_no = pd.Series(range(1, len(order) + 1), index=order.index)
    t["dev_no"] = t["developer_id"].map(dev_no)

    domain = t["developer_domain"].fillna("domain yok")
    t["developer_label"] = (t["developer"] + " (" + domain + ")").where(
        t["named"] == 1, "Geliştirici #" + t["dev_no"].astype(str)
    )
    cols = ["dev_no", "developer_label", "named", "is_generic", "genre", "is_game", "installs", "band_rank", "monetization", "n"]
    return t[cols].sort_values(["dev_no", "genre", "band_rank", "monetization"]).reset_index(drop=True)


if __name__ == "__main__":
    t = build()
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SUMMARY, index=False)
    print(f"Yazıldı: {SUMMARY.relative_to(ROOT)}, {len(t):,} satır, {SUMMARY.stat().st_size / 1e6:.2f} MB")
    print(f"Toplam uygulama (n toplamı): {t['n'].sum():,}")
    print(f"Geliştirici: {t['dev_no'].nunique():,}, adı görünen: {t.loc[t['named'] == 1, 'dev_no'].nunique():,}")
