"""Adım 5: temiz veriyi sql/schema.sql şemasına göre SQLite'a yükler."""
import sqlite3
from pathlib import Path

import pandas as pd

from clean import load_clean

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "apps.db"
SCHEMA = ROOT / "sql" / "schema.sql"

BOOL_COLS = ["free", "contains_ads", "offers_iap", "is_rated"]


def build_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    developers = (
        df[["developer", "developer_domain"]]
        .drop_duplicates()
        .sort_values(["developer", "developer_domain"], na_position="first")
        .reset_index(drop=True)
    )
    developers.insert(0, "developer_id", developers.index + 1)

    genres = df[["genre", "is_game"]].drop_duplicates().sort_values("genre")
    genres["is_game"] = genres["is_game"].astype(int)

    bands = df[["installs", "installs_min"]].drop_duplicates().sort_values("installs_min")
    bands.insert(1, "band_rank", range(1, len(bands) + 1))

    apps = df.merge(developers, on=["developer", "developer_domain"], how="left")
    apps[BOOL_COLS] = apps[BOOL_COLS].astype(int)
    for col in ["released", "last_updated"]:
        apps[col] = apps[col].dt.strftime("%Y-%m-%d")
    apps = apps[[
        "app_id", "title", "developer_id", "genre", "installs", "score", "ratings", "reviews",
        "free", "price", "currency", "contains_ads", "offers_iap", "content_rating", "released",
        "last_updated", "monetization", "is_rated", "release_year", "days_since_update",
    ]]
    return {"developers": developers, "genres": genres, "install_bands": bands, "apps": apps}


def load(db_path: Path = DB) -> None:
    tables = build_tables(load_clean())
    with sqlite3.connect(db_path) as con:
        con.executescript(SCHEMA.read_text())
        for name, table in tables.items():
            table.to_sql(name, con, if_exists="append", index=False)
        fk_errors = con.execute("PRAGMA foreign_key_check").fetchall()
    print(f"Yazıldı: {db_path.name}")
    for name, table in tables.items():
        print(f"  {name}: {len(table):,} satır")
    print(f"  foreign_key_check hatası: {len(fk_errors)}")


if __name__ == "__main__":
    load()
