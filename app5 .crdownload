import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정
st.set_page_config(page_title="축제 성과 분석 경영지원시스템", layout="wide")

st.title("📊 축제 예산 투자 대비 성과(ROI) 데이터 대시보드")
st.markdown("---")

# 2. 데이터셋 선언 (에러 방지를 위해 가장 단순한 리스트 구조 사용)
# [괄호 검증 완료]
data = [
    ["해운대모래축제", 48.11, 956273],
    ["대전 0시 축제", 38.10, 1753308],
    ["수원화성문화제", 18.62, 385900],
    ["해운대 빛축제", 14.53, 3787196],
    ["화순 고인돌축제", 11.63, 510483],
    ["광복로 겨울빛축제", 9.17, 2001843],
    ["유성국화축제", 4.32, 694038]
]

df = pd.DataFrame(data, columns=["축제명", "평균예산", "평균방문객수"])

# [정렬] 예산 높은 순(내림차순)
df = df.sort_values(by="평균예산", ascending=False)

# 3. [차트 1 섹션] 예산 순위 분석 및 SQL
st.subheader("📍 차트 1. TOP7 축제 3개년 평균 예산 순위")

# 차트 1용 SQL 쿼리 노출
sql_query_1 = """
/* 차트 1: 예산 테이블에서 축제별 3개년 평균 예산을 산출하여 내림차순 정렬 */
SELECT 
    축제명, 
    AVG(예산) AS '3개년_평균_예산_억원'
FROM 
    budget_table
GROUP BY 
    축제명
ORDER BY 
    AVG(예산) DESC;
"""
st.code(sql_query_1, language='sql')

# 차트 1 시각화 (가로 막대 그래프)
fig1 = px.bar(
    df,
    x="평균예산",
    y="축제명",
    orientation="h",
    text_auto=".2f",
    labels={"평균예산": "평균 예산(억원)", "축제명": "축제명"},
    color="평균예산",
    color_continuous_scale="Blues"
)
fig1.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# 4. [차트 2 섹션] 예산 vs 방문객 성과 및 JOIN SQL
st.subheader("📍 차트 2. 3개년 평균 예산 vs 방문객 성과 (이중축)")

# 차트 2용 JOIN SQL 쿼리 노출
sql_query_2 = """
/* 차트 2: 텍스트 정제를 통한 복합 JOIN으로 예산 대비 방문객 성과 산출 */
SELECT 
    b.축제명 AS '축제명',
    AVG(b.예산) AS '3개년_평균_예산_억원',
    AVG(v.전체방문객수) AS '3개년_평균_방문객수_명'
FROM 
    budget_table b
INNER JOIN 
    visitor_table v ON v.축제명 LIKE CONCAT('%', REPLACE(REPLACE(b.축제명, '2024 ', ''), '제61회 ', ''), '%') 
    AND b.연도 = v.연도
GROUP BY 
    b.축제명;
"""
st.code(sql_query_2, language='sql')

# 차트 2 시각화 (이중축 콤보 차트 - 괄호 매칭 철저 검증)
fig2 = make_subplots(specs=[[{"secondary_y": True}]])

# 막대 그래프: 예산 (왼쪽 Y축)
fig2.add_trace(
    go.Bar(
        x=df["축제명"],
        y=df["평균예산"],
        name="평균 예산(억원)",
        marker_color="rgba(135, 206, 250, 0.8)"
    ),
    secondary_y=False
)

# 선 그래프: 방문객수 (오른쪽 Y축)
fig2.add_trace(
    go.Scatter(
        x=df["축제명"],
        y=df["평균방문객수"],
        name="평균 방문객수(명)",
        mode="lines+markers+text",
        text=[f"{v/10000:.0f}만" for v in df["평균방문객수"]],
        textposition="top center",
        line=dict(color="firebrick", width=3)
    ),
    secondary_y=True
)

fig2.update_layout(
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=80, b=20)
)

fig2.update_yaxes(title_text="평균 예산 (억원)", secondary_y=False)
fig2.update_yaxes(title_text="평균 방문객 수 (명)", secondary_y=True)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# 5. 핵심 인사이트 출력 (요구사항 반영 고정 문구)
st.subheader("💡 데이터 분석 기반 최종 인사이트 (MIS 리포트)")

st.info("**① [데이터 기반 ROI 판정문]**: 상단 이중축 콤보 차트 분석 결과, 예산 투자 규모와 실제 방문객 수의 흐름이 일치하지 않으며, 이는 단순히 돈을 많이 쓴다고 해서 방문객이 비례하여 늘어나지 않음을 증명합니다.")

st.warning("**② [최고 가성비 및 리스크 축제 팩트 체크]**: 실제 3개년 평균 데이터를 기준으로 보면, 가장 효율적인 성과를 낸 가성비 우수 축제는 예산 투입 대비 방문객이 압도적인 **[해운대 빛축제]**인 반면, 투입 예산 대비 성과 개선이 필요한 축제는 **[해운대모래축제]**로 분석됩니다.")

st.success("**③ [경영정보시스템(MIS)적 최종 해결책 제언]**: 따라서 향후 지자체들은 무조건적인 예산 증액 경쟁을 중단해야 합니다. 단 하나의 축제를 열더라도 디지털 정보시스템(MIS) 기반의 체류형 인프라 연계, 빅데이터 타겟 마케팅, 그리고 지역 독점적 킬러 콘텐츠 개발 같은 '질적 요소'를 강화하는 방향으로 행정 체질을 개선해야 합니다.")