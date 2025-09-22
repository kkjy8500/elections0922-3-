
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="전략지역구 대시보드 (예시)", layout="wide")

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

def kpi_card(label, value, help_text=None):
    with st.container(border=True):
        st.markdown(f"##### {label}")
        st.markdown(f"<div style='font-size:28px; font-weight:700'>{value}</div>", unsafe_allow_html=True)
        if help_text:
            st.caption(help_text)

st.title("전략지역구 대시보드 (예시 데이터)")

# ---- Sidebar: data source & filters ----
with st.sidebar:
    st.header("데이터 불러오기 / 필터")
    uploaded = st.file_uploader("CSV 업로드 (예시 컬럼과 동일 형식)", type=["csv"])
    if uploaded is not None:
        df = load_data(uploaded)
    else:
        df = load_data("district_metrics_example.csv")
        st.caption("샘플: district_metrics_example.csv 사용 중")
    region_sel = st.multiselect("권역 선택", options=sorted(df["region"].dropna().unique()), default=[])
    winner_sel = st.multiselect("2024 승자(진영)", options=["진보","보수","기타"], default=[])
    sort_metric = st.selectbox("정렬 기준", ["competitiveness","volatility","prog_left_avg","voters_total","pct_old65","pct_young39","pct_40_50"])

# ---- Filtering ----
f = df.copy()
if region_sel:
    f = f[f["region"].isin(region_sel)]
if winner_sel:
    f = f[f["winner_2024"].isin(winner_sel)]

# ---- KPI Row ----
c1, c2, c3, c4, c5 = st.columns(5)
kpi_card("선거구 수", f"{len(f):,}")
kpi_card("평균 유권자 수", f"{int(f['voters_total'].mean()):,}" if len(f) else "-")
kpi_card("평균 고령층 비율(65+)", f"{f['pct_old65'].mean():.1f}%" if len(f) else "-")
kpi_card("평균 2030 여성 비율", f"{f['pct_fem_2030'].mean():.1f}%" if len(f) else "-")
kpi_card("평균 경합도(격차%)", f"{f['competitiveness'].mean():.1f}p" if len(f) else "-")

st.divider()

# ---- Layout: Left (환경) | Right (정치지형) ----
left, right = st.columns([1,1])

with left:
    st.subheader("선거환경")
    # Demographic bar chart
    demo_cols = ["pct_young39","pct_40_50","pct_old65","pct_fem_2030"]
    demo_long = f[["district_name"] + demo_cols].melt(id_vars="district_name", var_name="지표", value_name="비율")
    order = ["pct_young39","pct_40_50","pct_old65","pct_fem_2030"]
    name_map = {"pct_young39":"청년층(≤39)","pct_40_50":"40–50대","pct_old65":"65+","pct_fem_2030":"2030 여성"}
    demo_long["지표"] = demo_long["지표"].map(name_map)
    chart_demo = alt.Chart(demo_long).mark_bar().encode(
        x=alt.X("비율:Q", title="비율(%)"),
        y=alt.Y("district_name:N", sort=alt.SortField("district_name")),
        color="지표:N",
        tooltip=["district_name","지표","비율"]
    ).properties(height=400)
    st.altair_chart(chart_demo, use_container_width=True)

    # Scatter: 고령층 vs 진보 득표력
    st.caption("상관 관계(예시): 고령층 비율 ↔ 진보정당 득표력 평균")
    sc = alt.Chart(f).mark_circle(size=80).encode(
        x=alt.X("pct_old65:Q", title="고령층 비율(%)"),
        y=alt.Y("prog_left_avg:Q", title="진보정당 득표력 평균(%)"),
        tooltip=["district_name","pct_old65","prog_left_avg","winner_2024"]
    )
    st.altair_chart(sc, use_container_width=True)

with right:
    st.subheader("정치지형")
    # Competitiveness & Volatility table
    st.caption("경합도 낮음 → 우세 / 높음 → 박빙")
    top = f.sort_values(sort_metric, ascending=True if sort_metric in ["competitiveness","volatility"] else False)\
           [["district_name","region","winner_2024","competitiveness","volatility","prog_left_avg","voters_total"]].reset_index(drop=True)
    st.dataframe(top, use_container_width=True, hide_index=True)

    # Trend line (진영별 득표 추이)
    st.caption("정당성향별 득표 추이 (2018→2024)")
    trend_cols = ["prog_2018","prog_2020","prog_2022","prog_2024",
                  "cons_2018","cons_2020","cons_2022","cons_2024",
                  "oth_2018","oth_2020","oth_2022","oth_2024"]
    if len(f):
        # Pick or select districts
        pick = st.multiselect("선택 선거구 (최대 6개 권장)", options=f["district_name"].tolist(),
                              default=f["district_name"].head(3).tolist())
        tf = f[f["district_name"].isin(pick)].copy()
        # build long-form
        rows = []
        for _, r in tf.iterrows():
            for y in [2018, 2020, 2022, 2024]:
                rows.append({"district_name": r["district_name"], "year": y, "bloc":"진보", "vote": r[f"prog_{y}"]})
                rows.append({"district_name": r["district_name"], "year": y, "bloc":"보수", "vote": r[f"cons_{y}"]})
                rows.append({"district_name": r["district_name"], "year": y, "bloc":"기타", "vote": r[f"oth_{y}"]})
        tl = pd.DataFrame(rows)
        line = alt.Chart(tl).mark_line(point=True).encode(
            x=alt.X("year:O", title="연도"),
            y=alt.Y("vote:Q", title="득표율(%)", scale=alt.Scale(domain=[0,100])),
            color="bloc:N",
            facet="district_name:N",
            tooltip=["district_name","year","bloc","vote"]
        ).properties(width=250, height=180)
        st.altair_chart(line, use_container_width=True)

st.divider()
st.caption("Tip) 좌측 필터로 권역/승자/정렬 기준을 바꿔 보세요. CSV 업로드로 실제 데이터를 바로 적용할 수 있습니다.")
