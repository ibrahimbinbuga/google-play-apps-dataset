"""Adım 2: ham CSV'nin doğrulama raporu (şekil, tipler, eksik, tekrar, aykırı)."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "google_play_apps_2026_sample.csv"


def load_raw(path: Path = CSV) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def report(df: pd.DataFrame) -> None:
    print(f"Dosya boyutu: {CSV.stat().st_size:,} bayt ({CSV.stat().st_size / 1e6:.1f} MB)")
    print(f"Şekil: {df.shape[0]:,} satır x {df.shape[1]} sütun\n")

    print("== Tipler ve eksik değerler ==")
    summary = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "eksik": df.isna().sum(),
        "eksik_%": (df.isna().mean() * 100).round(2),
        "benzersiz": df.nunique(),
    })
    print(summary.to_string(), "\n")

    print("== Tekrarlar ==")
    print(f"Tam tekrarlı satır: {df.duplicated().sum():,}")
    print(f"Tekrarlı app_id: {df['app_id'].duplicated().sum():,}\n")

    print("== Boolean sütunların değerleri ==")
    for col in ["is_game", "free", "contains_ads", "offers_iap"]:
        print(col, df[col].value_counts(dropna=False).to_dict())
    print()

    print("== installs bantları ==")
    print(df["installs"].value_counts(dropna=False).to_string(), "\n")

    print("== Sayısal özet ==")
    print(df[["score", "ratings", "reviews", "price"]].describe().to_string(), "\n")

    print("== Aykırı kontroller ==")
    print(f"score 1-5 dışı: {((df['score'] < 1) | (df['score'] > 5)).sum():,}")
    print(f"score == 0: {(df['score'] == 0).sum():,}")
    print(f"ratings < 0: {(df['ratings'] < 0).sum():,}, reviews < 0: {(df['reviews'] < 0).sum():,}")
    print(f"reviews > ratings: {(df['reviews'] > df['ratings']).sum():,}")
    print(f"score var ama ratings boş/0: {(df['score'].notna() & ~(df['ratings'] > 0)).sum():,}")
    print(f"free=True ama price > 0: {((df['free'] == True) & (df['price'] > 0)).sum():,}")
    print(f"free=False ama price == 0 veya boş: {((df['free'] == False) & ~(df['price'] > 0)).sum():,}")
    print(f"price < 0: {(df['price'] < 0).sum():,}")
    paid = df.loc[df["price"] > 0, "price"]
    print(f"Ücretli fiyat yüzdelikleri: {paid.quantile([.5, .9, .99, 1]).round(2).to_dict()}")
    print("En pahalı 10:")
    print(df.nlargest(10, "price")[["app_id", "title", "genre", "price", "currency"]].to_string(), "\n")
    print("currency:", df["currency"].value_counts(dropna=False).to_dict(), "\n")

    print("== Tarihler ==")
    for col in ["released", "last_updated"]:
        d = pd.to_datetime(df[col], errors="coerce")
        bad = d.isna().sum() - df[col].isna().sum()
        print(f"{col}: min={d.min()}, max={d.max()}, parse edilemeyen={bad:,}")
    rel, upd = pd.to_datetime(df["released"], errors="coerce"), pd.to_datetime(df["last_updated"], errors="coerce")
    print(f"last_updated < released: {(upd < rel).sum():,}")
    print(f"last_updated > 2026-06-08: {(upd > '2026-06-08').sum():,}\n")

    print("== Kategorik ==")
    print(f"genre benzersiz: {df['genre'].nunique()}")
    print(df["genre"].value_counts(dropna=False).to_string(), "\n")
    print("content_rating:", df["content_rating"].value_counts(dropna=False).to_dict(), "\n")
    print("is_game x genre (oyun türleri):")
    print(df.loc[df["is_game"] == True, "genre"].value_counts().head(30).to_string())


if __name__ == "__main__":
    df = load_raw()
    print(df.head(3).T.to_string(), "\n")
    report(df)
