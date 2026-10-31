"""Adım 3: temizleme ve türetilmiş sütunlar. Her karar DEVLOG.md'de loglanır."""
from pathlib import Path

import pandas as pd

from validate import CSV, load_raw

ROOT = Path(__file__).resolve().parents[1]
CLEAN_CSV = ROOT / "data" / "apps_clean.csv"

# Tarama tarihi (7-8 Haziran 2026). Bugünün tarihi kullanılmaz.
REFERENCE_DATE = pd.Timestamp("2026-06-08")


def installs_to_int(band: pd.Series) -> pd.Series:
    """"1,000,000+" -> 1000000 (bandın alt sınırı)."""
    return band.str.replace(",", "", regex=False).str.rstrip("+").astype("int64")


def monetization(df: pd.DataFrame) -> pd.Series:
    """Ücretli uygulama reklam/IAP'ye bakılmadan `paid` olur (varsayım, DEVLOG)."""
    ads, iap = df["contains_ads"], df["offers_iap"]
    out = pd.Series("free_clean", index=df.index)
    out[ads & iap] = "ads_iap"
    out[ads & ~iap] = "ads_only"
    out[~ads & iap] = "iap_only"
    out[~df["free"]] = "paid"
    return out


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Sports hem oyun hem uygulama türü olarak geçiyor; oyunlar ayrı türe alınır.
    df.loc[(df["genre"] == "Sports") & df["is_game"], "genre"] = "Sports (Game)"

    df["released"] = pd.to_datetime(df["released"])
    df["last_updated"] = pd.to_datetime(df["last_updated"])
    df["ratings"] = df["ratings"].astype("Int64")
    df["reviews"] = df["reviews"].astype("Int64")

    df["installs_min"] = installs_to_int(df["installs"])
    df["monetization"] = monetization(df)
    df["is_rated"] = df["score"].notna()
    df["release_year"] = df["released"].dt.year.astype("Int64")
    df["days_since_update"] = (REFERENCE_DATE - df["last_updated"]).dt.days

    # Analizde kullanılmayan, kaynak sitesine giden link sütunu.
    return df.drop(columns=["fliar_profile_url"])


def load_clean() -> pd.DataFrame:
    return pd.read_csv(
        CLEAN_CSV,
        parse_dates=["released", "last_updated"],
        dtype={"ratings": "Int64", "reviews": "Int64", "release_year": "Int64"},
        low_memory=False,
    )


if __name__ == "__main__":
    raw = load_raw(CSV)
    df = clean(raw)
    df.to_csv(CLEAN_CSV, index=False)
    print(f"Yazıldı: {CLEAN_CSV.name}, {df.shape[0]:,} satır x {df.shape[1]} sütun")
    print(f"Silinen satır: {len(raw) - len(df):,}")
    print(f"Sports -> Sports (Game): {(df['genre'] == 'Sports (Game)').sum():,}")
    print(f"genre benzersiz: {df['genre'].nunique()}, her türde tek is_game: {(df.groupby('genre')['is_game'].nunique() == 1).all()}")
    print("\nmonetization:")
    m = df["monetization"].value_counts()
    print(pd.DataFrame({"n": m, "%": (m / len(df) * 100).round(2)}).to_string())
    paid = df["monetization"] == "paid"
    print(f"\nÜcretli + reklam: {(paid & df['contains_ads']).sum():,}, ücretli + IAP: {(paid & df['offers_iap']).sum():,} (ikisi de 'paid' sayıldı)")
    print(f"\ninstalls_min min/max: {df['installs_min'].min():,} / {df['installs_min'].max():,}")
    print(f"installs -> installs_min eşleşmesi tekil: {df.groupby('installs')['installs_min'].nunique().eq(1).all()}")
    print(f"is_rated: {df['is_rated'].sum():,} ({df['is_rated'].mean() * 100:.2f}%)")
    print(f"release_year boş: {df['release_year'].isna().sum():,}, aralık {df['release_year'].min()}-{df['release_year'].max()}")
    print(f"days_since_update min/medyan/max: {df['days_since_update'].min()} / {df['days_since_update'].median():.0f} / {df['days_since_update'].max()}")
    print(f"days_since_update < 0: {(df['days_since_update'] < 0).sum():,}")
    print(f"Son 12 ayda güncellenmemiş (>365 gün): {(df['days_since_update'] > 365).mean() * 100:.2f}%")
