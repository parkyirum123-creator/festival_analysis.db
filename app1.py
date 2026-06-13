import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="지역 축제 방문객 분석", layout="wide")

# 2. 데이터 불러오기 함수
def load_data():
    files = {
        "2023": "2023년 지역축제 방문자수.csv",
        "2024": "2024년 지역축제 방문자수.csv",
        "2025": "2025년 지역축제 방문자수.csv"
    }
    
    for year, file in files.items():
        if not os.path.exists(file):
            st.error(f"❌ 파일을 찾을 수 없습니다: {file}")
            st.stop()
            
    df23 = pd.read_csv(files["2023"])
    df24 = pd.read_csv(files["2024"])
    df25 = pd.read_csv(files["2025"])
    
    # 컬럼 표준화
    df23 = df23[['축제명', '전체방문객수']].rename(columns={'전체방문객수': '2023_방문객'})
    df24 = df24[['축제명', '전체방문객수']].rename(columns={'전체방문객수': '2024_방문객'})
    df25 = df25[['축제명', '전체방문객수']].rename(columns={'전체방문객수': '2025_방문객'})
    
    # Pandas를 이용한 Full Outer Join (SQL의 FULL OUTER JOIN과 동일)
    merged_df = pd.merge(df25, df24, on='축제명', how='outer')
    merged_df = pd.merge(merged_df, df23, on='축제명', how='outer')
    
    return merged_df

df = load_data()

# 3. 데이터 전처리 및 TOP 7 추출
for col in ['2023_방문객', '2024_방문객', '2025_방문객']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

top7 = df.sort_values(by='2025_방문객', ascending=False).head(7).copy()
top7['평균방문객'] = top7[['2023_방문객', '2024_방문객', '2025_방문객']].mean(axis=1)

for col in ['2023_방문객', '2024_방문객', '2025_방문객', '평균방문객']:
    top7[f'{col}_만명'] = (top7[col] / 10000).round(1)

# 4. 시각화 (Plotly)
st.title("📊 지역 축제 데이터 분석 대시보드")
st.subheader("지역 축제 방문객 TOP 7 — 3개년 추이 비교")

fig = go.Figure()
years = ['2023', '2024', '2025']
colors = ['#AB63FA', '#EF553B', '#00CC96']

for i, year in enumerate(years):
    col_name = f'{year}_방문객_만명'
    text_labels = []
    hover_labels = []
    
    for idx, row in top7.iterrows():
        val = row[col_name]
        name = row['축제명']
        if year == '2023' and "유성국화축제" in name and (pd.isna(val) or val == 0):
            text_labels.append("데이터 없음")
            hover_labels.append("데이터 없음")
        elif year == '2023' and "광복로" in name and val == 0:
            text_labels.append("0 (미개최)")
            hover_labels.append("미개최 (데이터 없음)")
        else:
            label = f"{val}만" if not pd.isna(val) else "데이터 없음"
            text_labels.append(label)
            hover_labels.append(f"{val}만 명" if not pd.isna(val) else "데이터 없음")

    fig.add_trace(go.Bar(
        x=top7['축제명'], y=top7[col_name], name=f'{year}년',
        marker_color=colors[i], text=text_labels, textposition='outside',
        customdata=hover_labels, hovertemplate='%{x}<br>' + f'{year}년: ' + '%{customdata}<extra></extra>'
    ))

fig.add_trace(go.Scatter(
    x=top7['축제명'], y=top7['평균방문객_만명'], name='3개년 평균',
    mode='lines+markers+text', line=dict(color='royalblue', width=4, dash='dot'),
    text=top7['평균방문객_만명'].apply(lambda x: f"<b>{x}만</b>"),
    textposition='top center'
))

fig.update_layout(xaxis_tickangle=-45, barmode='group', height=600)
st.plotly_chart(fig, use_container_width=True)

# 5. 하단 정보 및 SQL 로직 섹션
st.caption("출처: 문화체육관광부 지역축제 개최계획 현황 (2023~2025)")

# SQL 설명 섹션 추가
with st.expander("🔍 데이터 처리 로직 확인 (SQL Query)"):
    st.write("3개년 데이터를 '축제명' 기준으로 합치기 위해 사용된 SQL 로직입니다.")
    sql_code = """
/* 2023, 2024, 2025년 테이블을 '축제명' 기준으로 합침 */
SELECT 
    COALESCE(T5.축제명, T4.축제명, T3.축제명) AS 축제명,
    T3.전체방문객수 AS 방문객_2023,
    T4.전체방문객수 AS 방문객_2024,
    T5.전체방문객수 AS 방문객_2025,
    (T3.전체방문객수 + T4.전체방문객수 + T5.전체방문객수) / 3 AS 평균방문객
FROM FESTIVAL_2025 T5
FULL OUTER JOIN FESTIVAL_2024 T4 ON T5.축제명 = T4.축제명
FULL OUTER JOIN FESTIVAL_2023 T3 ON T5.축제명 = T3.축제명
ORDER BY T5.전체방문객수 DESC
LIMIT 7;
    """
    st.code(sql_code, language='sql')

col1, col2 = st.columns(2)
with col1:
    st.info("💡 **축제의 생명력 및 지속성 검증**\n\n3개년 동안 방문객이 꾸준히 유지되거나 성장한 축제를 식별합니다.")
with col2:
    st.info("🎯 **전국구 축제의 하한선(Baseline) 설정**\n\nTOP 7 축제의 최소 방문객 기준을 파악하여 벤치마크를 제공합니다.")
