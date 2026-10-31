"""Adım 7: figures/ altına kaydedilen grafikler. Her grafik başlık, eksen, birim, n ve okuma notu taşır."""
import sqlite3
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from load_db import DB

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"

# Gelir modeli sırası ve renkleri sabit (kategorik palet, sıra CVD için doğrulandı).
MONETIZATION = ["free_clean", "ads_only", "ads_iap", "iap_only", "paid"]
LABELS = {
    "free_clean": "Reklamsız, IAP'siz",
    "ads_only": "Yalnızca reklam",
    "ads_iap": "Reklam + IAP",
    "iap_only": "Yalnızca IAP",
    "paid": "Ücretli",
}
COLORS = dict(zip(MONETIZATION, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]))
SURFACE = "#fcfcfb"
TEXT, TEXT_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

SAMPLE_NOTE = "Kaynak: Google Play Apps 2026 örneklemi (Kaggle, fliarbi), tam verinin %9'u, geliştirici bazlı. ABD mağazası, Haziran 2026."
MIN_GENRE_N = 200

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT_2,
    "xtick.color": TEXT_2,
    "ytick.color": TEXT_2,
    "text.color": TEXT,
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

_PCT_COLS = ", ".join(f"100.0 * AVG(monetization = '{m}') AS {m}" for m in MONETIZATION)

SQL_BAND = f"""
SELECT
    CASE WHEN b.band_rank >= 10 THEN 10 ELSE b.band_rank END AS band_rank,
    CASE WHEN b.band_rank >= 10 THEN '50,000,000+' ELSE a.installs END AS installs,
    COUNT(*) AS n,
    {_PCT_COLS}
FROM apps AS a JOIN install_bands AS b USING (installs)
GROUP BY 1, 2 ORDER BY 1
"""

SQL_GENRE = f"""
SELECT genre, g.is_game, COUNT(*) AS n, {_PCT_COLS}
FROM apps JOIN genres AS g USING (genre)
GROUP BY genre HAVING COUNT(*) >= {MIN_GENRE_N}
"""

SQL_STALE = """
SELECT
    CASE WHEN b.band_rank >= 10 THEN 10 ELSE b.band_rank END AS band_rank,
    CASE WHEN b.band_rank >= 10 THEN '50,000,000+' ELSE a.installs END AS installs,
    COUNT(*) AS n,
    100.0 * AVG(a.days_since_update > 365) AS stale_pct
FROM apps AS a JOIN install_bands AS b USING (installs)
GROUP BY 1, 2 ORDER BY 1
"""

# Kurulum bandı grupları: <100K = bant 1-4, 100K-1M = bant 5-6, 1M+ = bant 7-15.
SIZE_GROUP_CASE = """CASE WHEN b.band_rank <= 4 THEN '<100K' WHEN b.band_rank <= 6 THEN '100K-1M' ELSE '1M+' END"""
FOCUS_GENRES = ["Productivity", "Finance", "Entertainment"]

SQL_FOCUS_SIZE = f"""
SELECT
    a.genre,
    {SIZE_GROUP_CASE} AS size_group,
    MIN(b.band_rank) AS first_rank,
    COUNT(*) AS n,
    {_PCT_COLS}
FROM apps AS a JOIN install_bands AS b USING (installs)
WHERE a.genre IN ({", ".join(f"'{g}'" for g in FOCUS_GENRES)})
GROUP BY a.genre, size_group
"""


def query(sql: str, db_path: Path = DB) -> pd.DataFrame:
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(sql, con)


def _finish(fig, ax, title: str, note: str, path: Path) -> None:
    # Başlık lejantın üstünde, okuma notu x ekseni etiketinin altında; ikisi de eksene bağlı.
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=30)
    ax.annotate(
        textwrap.fill(f"Okuma: {note}", 150) + f"\n{SAMPLE_NOTE}", xy=(0, 0), xycoords=("axes fraction", ax.xaxis.label), xytext=(0, -10),
        textcoords="offset points", ha="left", va="top", fontsize=8.5, color=TEXT_2,
    )
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def stacked_share(ax, table: pd.DataFrame, labels: list[str]) -> None:
    """%100 yığılmış yatay çubuk; ≥8% segmentlere doğrudan yüzde etiketi."""
    left = pd.Series(0.0, index=table.index)
    y = range(len(table))
    for m in MONETIZATION:
        ax.barh(y, table[m], left=left, color=COLORS[m], edgecolor=SURFACE, linewidth=1.5, height=0.72, label=LABELS[m])
        for i, (start, width) in enumerate(zip(left, table[m])):
            if width >= 8:
                ax.text(start + width / 2, i, f"{width:.0f}", ha="center", va="center", fontsize=8, color=TEXT)
        left += table[m]
    ax.set_yticks(list(y), labels)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Uygulama payı (%)")
    ax.set_ylim(len(table) - 0.5, -0.5)
    ax.legend(ncols=5, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, fontsize=9, handlelength=1.2)


def fig_band_monetization(path: Path = FIG_DIR / "01_band_monetization.png") -> pd.DataFrame:
    t = query(SQL_BAND)
    labels = [f"{b}  (n={n:,})" for b, n in zip(t["installs"], t["n"])]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    stacked_share(ax, t, labels)
    ax.set_ylabel("Kurulum bandı (alt sınır)")
    first, last = t.iloc[0], t.iloc[-1]
    _finish(
        fig, ax, "Kurulum bandı büyüdükçe reklam + IAP birlikte kullanan uygulamaların payı artıyor",
        f"1,000+ bandında reklamsız/IAP'siz uygulamalar %{first['free_clean']:.0f}, reklam + IAP %{first['ads_iap']:.0f}; "
        f"50M+ bantlarında bu oranlar %{last['free_clean']:.0f} ve %{last['ads_iap']:.0f}. 50M ve üstü bantlar küçük n nedeniyle birleştirildi.",
        path,
    )
    return t


def fig_genre_monetization(path: Path = FIG_DIR / "02_genre_monetization.png") -> pd.DataFrame:
    t = query(SQL_GENRE).sort_values("free_clean", ascending=False).reset_index(drop=True)
    labels = [f"{g}{' (oyun)' if game else ''}  (n={n:,})" for g, game, n in zip(t["genre"], t["is_game"], t["n"])]
    fig, ax = plt.subplots(figsize=(10, 14))
    stacked_share(ax, t, labels)
    ax.set_ylabel("Tür (n ≥ 200)")
    top, bottom = t.iloc[0], t.iloc[-1]
    _finish(
        fig, ax, "Oyun türlerinde reklamsız/IAP'siz uygulama nadir, iş ve finans türlerinde çoğunluk",
        f"En yüksek reklamsız/IAP'siz pay {top['genre']} (%{top['free_clean']:.0f}), en düşük {bottom['genre']} (%{bottom['free_clean']:.0f}). "
        f"{len(t)} tür, n < 200 olan 3 tür (Comics, Libraries & Demo, Music) dışarıda.",
        path,
    )
    return t


def fig_focus_genres(results_q10: pd.DataFrame, path: Path = FIG_DIR / "03_focus_genres.png") -> pd.DataFrame:
    t = results_q10.rename(columns={f"{m}_pct": m for m in MONETIZATION}).reset_index(drop=True)
    names = {"ALL": "Tüm veri"}
    labels = [f"{names.get(s, s)}  (n={n:,})" for s, n in zip(t["segment"], t["n"])]
    fig, ax = plt.subplots(figsize=(10, 3.4))
    stacked_share(ax, t, labels)
    ax.set_ylabel("Segment")
    f, e = t.set_index("segment").loc["Finance"], t.set_index("segment").loc["Entertainment"]
    _finish(
        fig, ax, "Finance ve Productivity çoğunlukla reklamsız, Entertainment reklama dayanıyor",
        f"Finance'ta reklamsız/IAP'siz pay %{f['free_clean']:.0f}, Entertainment'ta yalnızca reklam %{e['ads_only']:.0f} (tüm veride sırasıyla "
        f"%{t.iloc[-1]['free_clean']:.0f} ve %{t.iloc[-1]['ads_only']:.0f}).",
        path,
    )
    return t


def fig_stale_by_band(path: Path = FIG_DIR / "04_stale_by_band.png") -> pd.DataFrame:
    t = query(SQL_STALE)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    y = range(len(t))
    ax.barh(y, t["stale_pct"], color=COLORS["free_clean"], height=0.62)
    for i, (pct, n) in enumerate(zip(t["stale_pct"], t["n"])):
        ax.text(pct + 0.4, i, f"%{pct:.1f}", va="center", fontsize=8.5, color=TEXT)
    ax.set_yticks(list(y), [f"{b}  (n={n:,})" for b, n in zip(t["installs"], t["n"])])
    ax.invert_yaxis()
    ax.set_xlim(0, max(t["stale_pct"]) * 1.15)
    ax.set_xlabel("Son 12 ayda güncellenmemiş uygulama payı (%), referans 2026-06-08")
    ax.set_ylabel("Kurulum bandı (alt sınır)")
    _finish(
        fig, ax, "Küçük kurulum bantlarında güncellenmeyen uygulama payı daha yüksek",
        f"365 günden uzun süredir güncellenmemiş uygulama payı 1,000+ bandında %{t.iloc[0]['stale_pct']:.0f}, "
        f"50M+ bantlarında %{t.iloc[-1]['stale_pct']:.0f}. 50M ve üstü bantlar küçük n nedeniyle birleştirildi.",
        path,
    )
    return t


def fig_focus_by_size(path: Path = FIG_DIR / "05_focus_genres_by_size.png") -> pd.DataFrame:
    t = query(SQL_FOCUS_SIZE)
    t["genre_order"] = t["genre"].map({g: i for i, g in enumerate(FOCUS_GENRES)})
    t = t.sort_values(["genre_order", "first_rank"]).reset_index(drop=True)
    labels = [f"{g} · {s}  (n={n:,})" for g, s, n in zip(t["genre"], t["size_group"], t["n"])]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    stacked_share(ax, t, labels)
    for boundary in (2.5, 5.5):
        ax.axhline(boundary, color=TEXT_2, linewidth=0.8)
    ax.set_ylabel("Tür · kurulum bandı grubu")
    p = t.set_index(["genre", "size_group"])
    small = t.loc[t["n"] < MIN_GENRE_N, ["genre", "size_group", "n"]]
    small_note = "".join(f" {g} {s} grubunda n={n} (< {MIN_GENRE_N}), dikkatli okunmalı." for g, s, n in small.itertuples(index=False))
    _finish(
        fig, ax, "Productivity'de büyüdükçe reklamsız/IAP'siz pay düşüyor, Finance'ta düşmüyor",
        f"Productivity'de reklamsız/IAP'siz pay <100K grubunda %{p.loc[('Productivity', '<100K'), 'free_clean']:.0f}, "
        f"1M+ grubunda %{p.loc[('Productivity', '1M+'), 'free_clean']:.0f}; Finance'ta %{p.loc[('Finance', '<100K'), 'free_clean']:.0f} ve "
        f"%{p.loc[('Finance', '1M+'), 'free_clean']:.0f}. Gruplar: <100K = 1,000+ ile 50,000+ arası bantlar, 100K-1M = 100,000+ ve 500,000+, 1M+ = 1,000,000+ ve üstü."
        + small_note,
        path,
    )
    return t


if __name__ == "__main__":
    from queries import run

    FIG_DIR.mkdir(exist_ok=True)
    fig_band_monetization()
    fig_genre_monetization()
    fig_focus_genres(run("Q10"))
    fig_stale_by_band()
    fig_focus_by_size()
    print(*sorted(p.name for p in FIG_DIR.glob("*.png")), sep="\n")
