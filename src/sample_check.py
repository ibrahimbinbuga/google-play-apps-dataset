"""Adım 4: örneklem sağlaması. Kıyas değerleri REPORT.md'den (tam veri), bulgu değildir.

Sapma raporlanır, düzeltme (ağırlıklandırma) yapılmaz.
"""
import pandas as pd

from clean import load_clean

# Tam veri (1,101,050 uygulama) kıyas oranları, REPORT.md.
BENCHMARK = {"contains_ads": 43.0, "offers_iap": 18.0, "paid": 1.4}

GENERIC_DEVELOPER = "Individual developer"


def developer_key(df: pd.DataFrame) -> pd.Series:
    """Geliştirici kimliği = (developer, developer_domain) çifti."""
    return df["developer"] + " | " + df["developer_domain"].fillna("<no domain>")


def shares(df: pd.DataFrame) -> pd.DataFrame:
    sample = {
        "contains_ads": df["contains_ads"].mean() * 100,
        "offers_iap": df["offers_iap"].mean() * 100,
        "paid": (~df["free"]).mean() * 100,
    }
    out = pd.DataFrame({"örneklem_%": sample, "tam_veri_%": BENCHMARK})
    out["fark_puan"] = out["örneklem_%"] - out["tam_veri_%"]
    return out.round(2)


def top_developers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    counts = developer_key(df).value_counts()
    top = counts.head(n).to_frame("n_apps")
    top["pay_%"] = (top["n_apps"] / len(df) * 100).round(2)
    top["kümülatif_%"] = top["pay_%"].cumsum().round(2)
    return top


if __name__ == "__main__":
    df = load_clean()
    print("== Kıyas oranları ==")
    print(shares(df).to_string(), "\n")

    key = developer_key(df)
    counts = key.value_counts()
    print("== Geliştirici yoğunlaşması ==")
    print(f"Benzersiz geliştirici (developer, domain): {counts.size:,}")
    print(f"Geliştirici başına uygulama: medyan {counts.median():.0f}, ortalama {counts.mean():.2f}, max {counts.max():,}")
    print(f"Tek uygulamalı geliştirici: {(counts == 1).sum():,} ({(counts == 1).mean() * 100:.1f}%)")
    for k in [10, 100, 1000]:
        print(f"En büyük {k} geliştiricinin payı: {counts.head(k).sum() / len(df) * 100:.2f}%")
    print(f"\nEn büyük 10 geliştirici:\n{top_developers(df).to_string()}\n")

    generic = df["developer"] == GENERIC_DEVELOPER
    print(f"'{GENERIC_DEVELOPER}' satırları: {generic.sum():,}, bunların domain'siz olanı: {(generic & df['developer_domain'].isna()).sum():,}")

    print("\n== Duyarlılık: en büyük 10 geliştirici çıkarılınca ==")
    rest = df[~key.isin(counts.head(10).index)]
    print(f"Kalan satır: {len(rest):,}")
    print(shares(rest).to_string())
