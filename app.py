import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- [0. 페이지 설정] ---
st.set_page_config(page_title="지역축제 방문객 동적 분석", layout="wide")

# --- [1. 데이터 연동 및 전처리 함수] ---
def load_data():
    """
    실제 SQLite DB 연동 및 전처리
    파일이 없을 경우를 대비해 Mock Data 생성 로직 포함
    """
    try:
        conn = sqlite3.connect('축제방문자수.db')
        # DB에서 데이터 읽기 (SQL 쿼리)
        query = "SELECT 광역자치단체명, 축제명, 방문객수, 연도 FROM 지역축제3개년"
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception:
        # 실제 DB 파일이 없는 경우를 위한 시연용 가상 데이터 구조 (요구사항 반영)
        data = {
            '광역자치단체명': ['서울', '경기', '강원', '제주', '경남', '부산', '인천', '전남', '경북', '충남', '전북', '충북', '대구', '대전', '울산', '광주', '세종'] * 3,
            '연도': [2023] * 17 + [2024] * 17 + [2025] * 17,
            '방문객수': [
                # 2023년 가상 데이터 (수도권/관광지 높음)
                9000000, 9500000, 6000000, 5500000, 4500000, 4000000, 3500000, 3000000, 2800000, 2500000, 2200000, 2000000, 1800000, 1500000, 1200000, 1000000, 500000,
                # 2024년 데이터 (수치 변화)
                9200000, 9800000, 6200000, 5800000, 4700000, 4200000, 3700000, 3100000, 2900000, 2600000, 2300000, 2100000, 1900000, 1600000, 1300000, 1100000, 600000,
                # 2025년 데이터
                9500000, 10500000, 6500000, 6100000, 4900000, 4400000, 3900000, 3300000, 3100000, 2800000, 2500000, 2300000, 2100000, 1800000, 1500000, 1300000, 800000
            ]
        }
        df = pd.DataFrame(data)
    
    # [참고] 만약 CSV 파일로 연동하고 싶다면 아래 주석을 해제하세요.
    # df = pd.read_csv('your_data.csv') 
    
    return df

# 데이터 로드
df_raw = load_data()

# --- [2. UI 레이아웃 및 필터] ---
st.title("📊 대한민국 지자체별 연간 축제 총 방문자 수 현황")
st.markdown("전국 17개 광역자치단체의 3개년 데이터를 기반으로 축제 성과를 분석합니다.")

# 필터 영역
st.divider()
selected_year = st.selectbox(
    "조회 연도 선택",
    ["2023년", "2024년", "2025년", "3개년 평균"],
    index=1
)

# --- [3. 데이터 필터링 및 집계] ---
if selected_year == "3개년 평균":
    # 3개년 평균 계산: 먼저 지역/연도별 합계를 구한 뒤, 지역별 평균을 냄
    df_yearly_sum = df_raw.groupby(['광역자치단체명', '연도'])['방문객수'].sum().reset_index()
    df_filtered = df_yearly_sum.groupby('광역자치단체명')['방문객수'].mean().reset_index()
    display_title = "지역별 연간 축제 방문자 수 (3개년 평균)"
else:
    # 선택된 특정 연도 필터링
    year_int = int(selected_year[:4])
    df_filtered = df_raw[df_raw['연도'] == year_int].groupby('광역자치단체명')['방문객수'].sum().reset_index()
    display_title = f"지역별 연간 축제 방문자 수 ({year_int}년)"

# X축 순서 고정 (서울, 부산, 대구... 제주 순)
fixed_order = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
df_filtered['광역자치단체명'] = pd.Categorical(df_filtered['광역자치단체명'], categories=fixed_order, ordered=True)
df_filtered = df_filtered.sort_values('광역자치단체명')

# --- [4. 차트 시각화 (Plotly)] ---
fig = px.bar(
    df_filtered,
    x='광역자치단체명',
    y='방문객수',
    title=display_title,
    labels={'방문객수': '총 방문자 수 (명)', '광역자치단체명': '지역명'},
    text_auto='.2s',
    color='방문객수',
    color_continuous_scale='Blues'
)

fig.update_layout(
    xaxis_title="",
    yaxis_title="방문객 합계 (명)",
    margin=dict(l=20, r=20, t=60, b=20),
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# --- [5. 동적 인사이트 추출 로직] ---
# 수치 기반 상위 3개 지역과 하위 3개 지역 추출
top_3 = df_filtered.nlargest(3, '방문객수')['광역자치단체명'].tolist()
bottom_3 = df_filtered.nsmallest(3, '방문객수')['광역자치단체명'].tolist()

# 인사이트 텍스트 구성
st.divider()
st.subheader("📋 데이터 기반 전략 분석 가이드라인")

# 동적 텍스트 생성
fact_text = f"**① [데이터 팩트 분석]**: 현재 **{selected_year}** 기준으로 데이터를 분석한 결과, 가장 방문자 수가 많은 상위 지역은 **{', '.join(top_3)}**이며, 반대로 수치가 낮거나 질적 개선이 시급한 하위 지역은 **{', '.join(bottom_3)}**으로 나타납니다."

st.info(fact_text)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ✅ 우수 지역 벤치마킹 방식")
    st.success(f"""
    **대상: {', '.join(top_3)} 등 상위권 지역**
    - **브랜드화 성공**: 단순 일회성 행사를 넘어 지역의 정체성을 담은 독보적 브랜드 구축 사례 분석.
    - **수익형 비즈니스**: 축제를 단순 관람형에서 지역 특산물 수출 및 유통 채널과 연계하여 직접적인 경제 효과를 창출하는 모델 적용.
    - **체류형 콘텐츠**: 광역 단위 연계 관광 코스 개발을 통한 체류 시간 극대화 전략.
    """)

with col2:
    st.markdown("#### ⚠️ 낮은 지역 개선 방식")
    st.warning(f"""
    **대상: {', '.join(bottom_3)} 등 하위권 지역**
    - **양적 구조조정**: 관성적으로 추진되던 소규모/유사 축제들을 과감히 통폐합하여 예산 효율성 제고.
    - **데이터 기반 마케팅**: 무분별한 홍보 대신 정보시스템(통신사/카드 데이터) 기반의 타겟 고객 분석 및 마케팅 집중.
    - **인프라 재배정**: 축제 예산의 일부를 스마트 관광 안내 시스템 및 체류형 인프라(숙박, 교통) 고도화에 재투자하는 질적 전환 필요.
    """)