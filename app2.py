import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="지역별 축제 및 방문객 분석", page_icon="🎉", layout="wide")

st.title("🎉 2025 대한민국 지역별 축제 수 및 방문객 수 분석 대시보드")
st.markdown("---")

db_path = "festival.db"

if not Path(db_path).exists():
    st.error("""
❌ festival.db 파일을 찾을 수 없습니다.

1. app.py와 festival.db가 같은 폴더에 있는지 확인하세요.
2. 파일명이 festival.db인지 확인하세요.
""")
    st.stop()

sql_query = """
SELECT
    f.지역,
    f.총축제수,
    v.총방문객수
FROM festival_count f
JOIN visitor_count v
ON f.지역 = v.지역
"""

conn = sqlite3.connect(db_path)
df = pd.read_sql_query(sql_query, conn)
conn.close()

region_order = [
    "서울","부산","대구","인천","광주","대전","울산","세종",
    "경기","강원","충북","충남","전북","전남","경북","경남","제주"
]

df["지역"] = pd.Categorical(df["지역"], categories=region_order, ordered=True)
df = df.sort_values("지역")

st.header("📊 전국 지역별 축제 수 및 방문객 수 비교")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df["지역"],
        y=df["총축제수"],
        name="축제 수"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["지역"],
        y=df["총방문객수"],
        mode="lines+markers",
        name="방문객 수",
        yaxis="y2"
    )
)

fig.update_layout(
    title="2025 지역별 축제 수 및 방문객 수",
    yaxis=dict(title="축제 수(개)"),
    yaxis2=dict(title="방문객 수(명)", overlaying="y", side="right"),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("① 사용한 SQL")
st.code(sql_query, language="sql")

st.subheader("② 인사이트")

max_festival = df.loc[df["총축제수"].idxmax()]
max_visitor = df.loc[df["총방문객수"].idxmax()]

st.info(
    f"""
축제 수가 가장 많은 지역은 {max_festival['지역']} ({max_festival['총축제수']}개)입니다.

방문객 수가 가장 많은 지역은 {max_visitor['지역']} ({max_visitor['총방문객수']:,}명)입니다.

축제 수와 방문객 수의 관계를 비교하여 지역 관광 경쟁력을 분석할 수 있습니다.
"""
)

st.subheader("③ 조회 데이터")
st.dataframe(df, use_container_width=True)
