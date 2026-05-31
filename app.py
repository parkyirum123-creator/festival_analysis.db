import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- [0. 페이지 설정] ---
st.set_page_config(page_title="지방 지자체 축제 방문객 분석", layout="wide")

# --- [1. 화면 상단 SQL 쿼리 노출] ---
st.subheader("📋 데이터 추출 쿼리 가이드")
sql_code = """
SELECT 
    year AS '연도',
    region AS '지자체',
    SUM(visitor_count) AS '총_방문자_수'
FROM 
    festival_db_table
WHERE 
    year IN (2023, 2024, 2025)
    AND region NOT IN ('서울', '경기', '인천')
GROUP BY 
    year, region;
"""
st.code(sql_code, language='sql')

# --- [2. 테스트용 가상 데이터(Mock Data) 생성] ---
@st.cache_data
def get_mock_data():
    # 수도권 제외 지방 14개 지자체 리스트
    regions = ['부산', '대구', '광주', '대전', '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
    years = [2023, 2024, 2025]
    
    data = []
    for year in years:
        for region in regions:
            # 연도별/지역별로 순위가 변동되도록 가변적인 수치 세팅
            # 랜덤성을 부여하되 특정 지역이 상위/하위권에 머물도록 가중치 조절
            if region in ['강원', '제주', '경남']:
                base = 5000000 + (year - 2023) * 500000
            elif region in ['세종', '울산', '광주']:
                base = 800000 + (year - 2023) * 100000
            else:
                base = 2500000 + (year - 2023) * 200000
                
            visitor_count = base + np.random.randint(-300000, 300000)
            data.append({'연도': year, '지자체': region, '총_방문자_수': visitor_count})
            
    return pd.DataFrame(data)

df_raw = get_mock_data()

# --- [3. 시각화 및 데이터 전처리] ---
st.divider()
st.title("🏞️ 수도권 제외 지방 지자체 축제 방문객 성과 대시보드")

# 상단 연도 선택 필터
selected_option = st.selectbox(
    "조회할 연도를 선택하세요 (수도권 제외 지방 14개 지자체 대상)",
    ["2023년", "2024년", "2025년", "3개년 평균"]
)

# 데이터 필터링 및 집계
if selected_option == "3개년 평균":
    df_filtered = df_raw.groupby('지자체')['총_방문자_수'].mean().reset_index()
    display_year = "3개년 평균"
else:
    year_val = int(selected_option[:4])
    df_filtered = df_raw[df_raw['연도'] == year_val].copy()
    display_year = f"{year_val}년"

# [핵심 요구사항] 방문자 수 많은 순서로 내림차순 정렬
df_filtered = df_filtered.sort_values(by='총_방문자_수', ascending=False)

# --- [4. 차트 시각화 (Plotly)] ---
fig = px.bar(
    df_filtered,
    x='지자체',
    y='총_방문자_수',
    title=f"[{display_year}] 지방 지자체별 방문자 수 순위 (내림차순 정렬)",
    labels={'총_방문자_수': '총 방문자 수 (명)', '지자체': '지방 광역자치단체'},
    text_auto='.3s',
    color='총_방문자_수',
    color_continuous_scale='Plasma' # 시각적 대비가 뚜렷한 컬러셋
)

# 차트 레이아웃 조정 (X축 정렬 상태 유지)
fig.update_layout(xaxis={'categoryorder':'total descending'}, height=500)
st.plotly_chart(fig, use_container_width=True)

# --- [5. 동적 인사이트 자동 추출 및 출력] ---
# 상위 3개 및 하위 3개 지역 자동 추출
top_3_list = df_filtered.nlargest(3, '총_방문자_수')['지자체'].tolist()
bottom_3_list = df_filtered.nsmallest(3, '총_방문자_수')['지자체'].tolist()

top_3_str = ", ".join(top_3_list)
bottom_3_str = ", ".join(bottom_3_list)

st.divider()
st.subheader("💡 데이터 기반 동적 분석 보고서")

# ① 지방 데이터 팩트 분석
st.markdown(f"""
**① [지방 데이터 팩트 분석]**  
현재 **{display_year}** 기준 수도권을 제외한 순수 지방 지역들을 많은 순서대로 정렬한 결과, 상위권에서 독보적인 유입 성과를 보이는 지역은 **[{top_3_str}]**이며, 반대로 방문자 수 유입 개선이 가장 시급한 하위권 지역은 **[{bottom_3_str}]**으로 나타납니다.
""")

# ② 많은 지역(지방 상위권) 벤치마킹 방식
st.success(f"""
**② [많은 지역(지방 상위권) 벤치마킹 방식]**  
데이터 상위권에 배치된 **[{top_3_str}]** 등의 성공 요인은 단순 일회성 행사가 아닌 지역 특색의 브랜드화에 있습니다. 타 지자체들은 단순히 축제 프로그램을 모방할 것이 아니라, 이들 성공 지역처럼 축제 유동인구를 '지역 상품 해외 수출 채널(무역 비즈니스)' 및 '글로벌 유통망'과 결합시키는 비즈니스 융합 모델을 필수적으로 벤치마킹해야 합니다.
""")

# ③ 낮은 지역(지방 하위권) 개선 방식
st.warning(f"""
**③ [낮은 지역(지방 하위권) 개선 방식]**  
상대적으로 수치가 저조한 **[{bottom_3_str}]** 등의 지자체들은 매년 관성적으로 집행하던 소규모 축제들을 과감하게 폐지 및 통폐합하는 '양적 구조조정'을 단행해야 합니다. 그 후 잔여 예산을 바탕으로, 정보시스템(MIS) 기반의 체류형 관광 인프라(지정 숙박앱 연계, 스마트 교통망) 구축과 빅데이터 타겟 홍보에 올인하여 '단 1개를 열더라도 하루 자고 가게 만드는 질적 체질 개선'을 이루어야 합니다.
""")

st.caption("※ 본 데이터는 분석 환경 테스트를 위한 가상 데이터(Mock Data)를 기반으로 생성되었습니다.")