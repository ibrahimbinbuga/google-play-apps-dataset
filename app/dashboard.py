"""Adım 8: Google Play gelir modeli dashboard'u (yerel). Çalıştır: streamlit run app/dashboard.py

Ham satırlar data/apps.db'den okunur. Herkese açık yayın için yalnızca özet tablolar kullanılmalı (İbrahim'e sorulacak).
"""
import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "apps.db"

MONETIZATION = ["free_clean", "ads_only", "ads_iap", "iap_only", "paid"]
LABELS = {
    "free_clean": "Reklamsız, IAP'siz",
    "ads_only": "Yalnızca reklam",
    "ads_iap": "Reklam + IAP",
    "iap_only": "Yalnızca IAP",
    "paid": "Ücretli",
}
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
MIN_GENRE_N = 200
GENERIC_DEVELOPER = "Individual developer"

st.set_page_config(page_title="Google Play gelir modeli", layout="wide")


@st.cache_data
def load() -> pd.DataFrame:
    sql = """
        SELECT a.app_id, a.genre, g.is_game, a.installs, b.band_rank, a.monetization,
               d.developer_id, d.developer, d.developer_domain
        FROM apps AS a
        JOIN genres AS g USING (genre)
        JOIN install_bands AS b USING (installs)
        JOIN developers AS d USING (developer_id)
    """
    with sqlite3.connect(DB) as con:
        df = pd.read_sql_query(sql, con)
    df["monetization_label"] = df["monetization"].map(LABELS)
    df["is_generic"] = (df["developer"] == GENERIC_DEVELOPER) & df["developer_domain"].isna()
    return df


def share_table(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """by × gelir modeli: n, pay (%) ve grup toplamı."""
    t = df.groupby([by, "monetization_label"]).size().rename("n").reset_index()
    t["group_n"] = t.groupby(by)["n"].transform("sum")
    t["pct"] = (t["n"] / t["group_n"] * 100).round(1)
    t["axis_label"] = t[by].astype(str) + "  (n=" + t["group_n"].map("{:,}".format) + ")"
    t["order"] = t["monetization_label"].map({LABELS[m]: i for i, m in enumerate(MONETIZATION)})
    return t


def stacked_chart(t: pd.DataFrame, sort: list[str], y_title: str) -> alt.Chart:
    color = alt.Color(
        "monetization_label:N",
        title="Gelir modeli",
        scale=alt.Scale(domain=[LABELS[m] for m in MONETIZATION], range=COLORS),
        legend=alt.Legend(orient="top"),
    )
    return (
        alt.Chart(t)
        .mark_bar(stroke="white", strokeWidth=1)
        .encode(
            x=alt.X("pct:Q", stack="normalize", title="Uygulama payı (%)", axis=alt.Axis(format="%")),
            y=alt.Y("axis_label:N", sort=sort, title=y_title),
            color=color,
            order=alt.Order("order:Q"),
            tooltip=[
                alt.Tooltip("axis_label:N", title="Grup"),
                alt.Tooltip("monetization_label:N", title="Gelir modeli"),
                alt.Tooltip("pct:Q", title="Pay (%)"),
                alt.Tooltip("n:Q", title="Uygulama", format=","),
            ],
        )
        .properties(height=max(220, 24 * len(sort)))
    )


df = load()

st.title("Google Play'de gelir modeli: tür ve kurulum bandı")
st.warning(
    "**Tam verinin %9'u, geliştirici bazlı örneklem.** Seçilen geliştiricilerin tüm uygulamaları dahil, "
    "rastgele uygulama örneği değil. ABD mağazası, Haziran 2026, yalnızca Android. "
    "Oranlar ilişki gösterir, neden-sonuç değil."
)

# Filtreler tek satırda.
c1, c2, c3 = st.columns([3, 1, 3])
genres = sorted(df["genre"].unique())
bands = df.drop_duplicates("installs").sort_values("band_rank")["installs"].tolist()
with c1:
    sel_genres = st.multiselect("Tür", genres, placeholder="Tümü")
with c2:
    sel_game = st.radio("Tip", ["Tümü", "Oyun", "Uygulama"], horizontal=True)
with c3:
    sel_bands = st.multiselect("Kurulum bandı", bands, placeholder="Tümü")

f = df
if sel_genres:
    f = f[f["genre"].isin(sel_genres)]
if sel_game != "Tümü":
    f = f[f["is_game"] == (1 if sel_game == "Oyun" else 0)]
if sel_bands:
    f = f[f["installs"].isin(sel_bands)]

st.caption(f"Seçimdeki uygulama sayısı: n = {len(f):,} / {len(df):,}")
if f.empty:
    st.info("Bu filtrelerle uygulama yok.")
    st.stop()

tab_genre, tab_band, tab_dev = st.tabs(["Tür × gelir modeli", "Kurulum bandı × gelir modeli", "Geliştirici yoğunlaşması"])

with tab_genre:
    t = share_table(f, "genre")
    small = sorted(t.loc[t["group_n"] < MIN_GENRE_N, "genre"].unique())
    t = t[t["group_n"] >= MIN_GENRE_N]
    if t.empty:
        st.info(f"Seçimde n ≥ {MIN_GENRE_N} olan tür yok.")
    else:
        free = t[t["monetization_label"] == LABELS["free_clean"]].set_index("axis_label")["pct"]
        sort = free.reindex(t["axis_label"].unique()).fillna(0).sort_values(ascending=False).index.tolist()
        st.subheader("Türe göre gelir modeli dağılımı")
        st.altair_chart(stacked_chart(t, sort, f"Tür (n ≥ {MIN_GENRE_N})"), width="stretch")
        st.caption(
            f"Okuma: türler reklamsız/IAP'siz uygulama payına göre büyükten küçüğe sıralı. "
            f"{t['genre'].nunique()} tür, n = {int(t['n'].sum()):,} uygulama."
        )
    if small:
        st.caption(f"n < {MIN_GENRE_N} olduğu için gösterilmeyen türler: {', '.join(small)}")

with tab_band:
    t = share_table(f, "installs")
    sort = [lbl for b in bands for lbl in t.loc[t["installs"] == b, "axis_label"].unique()]
    st.subheader("Kurulum bandına göre gelir modeli dağılımı")
    st.altair_chart(stacked_chart(t, sort, "Kurulum bandı (alt sınır)"), width="stretch")
    st.caption(
        f"Okuma: bant alt sınırı küçükten büyüğe. Bantlar tam sayı değil, geniş aralık (1,000,000+ ≈ 1M-5M). "
        f"n < {MIN_GENRE_N} olan bantların yüzdeleri dalgalı, n'e bakarak okuyun. n = {len(f):,}."
    )

with tab_dev:
    st.subheader("Geliştirici yoğunlaşması")
    counts = f.groupby(["developer_id", "developer", "developer_domain", "is_generic"], dropna=False).size().rename("n_apps").reset_index()
    named = counts[~counts["is_generic"]].sort_values("n_apps", ascending=False)
    generic_n = int(counts.loc[counts["is_generic"], "n_apps"].sum())
    top10 = named.head(10).copy()
    top10["pct"] = (top10["n_apps"] / len(f) * 100).round(2)
    top10["label"] = top10["developer"] + " (" + top10["developer_domain"].fillna("domain yok") + ")"

    m1, m2, m3 = st.columns(3)
    m1.metric("Geliştirici (developer, domain)", f"{len(counts):,}")
    m2.metric("En büyük 10 geliştiricinin payı (genel etiket hariç)", f"%{top10['n_apps'].sum() / len(f) * 100:.2f}")
    m3.metric(f"'{GENERIC_DEVELOPER}' (genel etiket)", f"{generic_n:,} uygulama")

    chart = (
        alt.Chart(top10)
        .mark_bar(color=COLORS[0], cornerRadiusEnd=3)
        .encode(
            x=alt.X("n_apps:Q", title="Uygulama sayısı"),
            y=alt.Y("label:N", sort="-x", title="Geliştirici"),
            tooltip=[
                alt.Tooltip("label:N", title="Geliştirici"),
                alt.Tooltip("n_apps:Q", title="Uygulama", format=","),
                alt.Tooltip("pct:Q", title="Seçimdeki pay (%)"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")
    st.caption(
        f"Okuma: '{GENERIC_DEVELOPER}' farklı kişileri birleştiren genel bir etiket olduğu için sıralamaya alınmadı. "
        f"Aynı şirket farklı domain ile ayrı geliştirici sayılabilir (örn. WABiz). n = {len(f):,}."
    )

    st.markdown("**En büyük 10 geliştiricinin gelir modeli** (tek tip gelir modeli tür oranlarını kaydırabilir)")
    mix = (
        f[f["developer_id"].isin(top10["developer_id"])]
        .merge(top10[["developer_id", "label"]], on="developer_id")
        .pivot_table(index="label", columns="monetization_label", values="app_id", aggfunc="count", fill_value=0)
    )
    mix = (mix.div(mix.sum(axis=1), axis=0) * 100).round(1)
    mix = mix[[LABELS[m] for m in MONETIZATION if LABELS[m] in mix.columns]]
    st.dataframe(mix.loc[top10["label"]], width="stretch")
