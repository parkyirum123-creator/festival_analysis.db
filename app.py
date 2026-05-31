import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- 0. 페이지 설정 ---
st.set_page_config(page_title="지역축제 방문자 분석", layout="wide")

# --- 1. 데이터베이스 연결 및 데이터 로드 함수 ---
def get_data_from_db():
    conn = sqlite3.connect('축제방문자수.db')
    
    # [참고] DB가 비어있을 경우를 대비한 가상 데이터 삽입 로직 (실제 파일이 있으면 무시됨)
    check_table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='지역축제3개년'").fetchone()
    if not check_table:
        # 가상 데이터 생성 (요구사항 반영: 수도권 및 관광강세 지역 차별화)
        regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        years = [2023, 2024, 2025]
        mock_data = []
        for y in years:
            for r in regions:
                # 연도별/지역별로 확연히 다른 수치 세팅
                if r in ['서울', '경기']: base = 8000000
                elif r in ['강원', '제주', '경남']: base = 5000000
                else: base = 1500000
                
                # 연도별로 10~20%씩 차이가 나도록 설정
                visitor_sum = int(base * (1 + (y - 2024) * 0.15)) 
                mock_data.append([r, f"{r} 축제", visitor_sum, y])
        
        df_mock = pd.DataFrame(mock_data, columns=['광역자치단체명', '축제명', '방문객수', '연도'])
        df_mock.to_sql('지역축제3개년', conn, index=False)

    # 데이터 불러오기
    query = "SELECT * FROM 지역축제3개년"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 데이터 가져오기
df_raw = get_data_from_db()

# --- 2. UI 레이아웃: 상단 타이틀 ---
st.title("🇰🇷 대한민국 지자체별 연간 축제 총 방문자 수 현황 (3개년)")
st.markdown("전국 17개 광역자치단체의 축제 방문객 데이터를 연도별로 비교 분석합니다.")

# --- 3. 데이터 전처리 및 필터링 ---
# 상단 필터 (2023, 2024, 2025, 3개년 평균)
st.divider()
selected_option = st.selectbox(
    "조회하고 싶은 연도를 선택하세요",
    ["2023년", "2024년", "2025년", "3개년 평균"],
    index=1 # 기본값 2024년
)

# 필터링 로직
if selected_option == "3개년 평균":
    # 지역별로 연도와 상관없이 평균 계산
    df_filtered = df_raw.groupby('광역자치단체명')['방문객수'].mean().reset_index()
    chart_title = "지역별 축제 방문자 수 (3개년 평균)"
else:
    # 선택된 연도 숫자만 추출 (예: '2023년' -> 2023)
    year_val = int(selected_option[:4])
    # Pandas 필터링: Year == selected_year
    df_filtered = df_raw[df_raw['연도'] == year_val].groupby('광역자치단체명')['방문객수'].sum().reset_index()
    chart_title = f"지역별 축제 방문자 수 ({year_val}년)"

# X축 순서 고정 (요구사항: 서울 ~ 제주 순서)
fixed_order = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
df_filtered['광역자치단체명'] = pd.Categorical(df_filtered['광역자치단체명'], categories=fixed_order, ordered=True)
df_filtered = df_filtered.sort_values('광역자치단체명')

# --- 4. 시각화 (Plotly Bar Chart) ---
fig = px.bar(
    df_filtered,
    x='광역자치단체명',
    y='방문객수',
    title=chart_title,
    labels={'방문객수': '총 방문자 수 (명)', '광역자치단체명': '지역'},
    text_auto='.2s', # 숫자 단위 자동 축약 (ex: 8.5M)
    color='방문객수',
    color_continuous_scale='GnBu' # 청록색 계열의 세련된 색상
)

# 차트 디테일 설정
fig.update_layout(
    xaxis_tickangle=0,
    title_font_size=22,
    margin=dict(l=20, r=20, t=60, b=20),
    height=500
)

# 차트 출력
st.plotly_chart(fig, use_container_width=True)

# --- 5. 하단 분석 결과 및 인사이트 (st.info 활용) ---
st.divider()
st.subheader("📋 분석 결과 및 전략 제언")

insight_text = """
**① [데이터 팩트] 3개년 전국 축제 방문자 추이**  
수도권 제외 상위권인 **강원, 제주, 경남** 등은 매년 안정적인 방문객 유치를 보여주며 지역 관광의 핵심 축 역할을 하고 있습니다.

**② [많은 지역 벤치마킹 방식] 성과 우수 지역 우수사례 도입**  
단순 행사가 아닌 **지역 특색의 브랜드화**가 시급합니다. 축제를 단순 구경거리에서 탈피시켜 지역 상품 수출 및 유통 채널과 연계하는 **비즈니스 모델 중심의 벤치마킹**이 필요합니다.

**③ [낮은 지역 개선 방식] 하위권 지자체의 질적 전환**  
성과가 미비한 관성적인 소규모 축제들을 과감히 **통폐합(양적 구조조정)**해야 합니다. 여기서 확보된 예산을 정보시스템 기반의 **체류형 관광 인프라** 구축 및 **빅데이터 타겟 마케팅**에 집중 투입하는 질적 체질 개선이 시급합니다.
"""

st.info(insight_text)

# 사용된 쿼리 표시 (학습용)
with st.expander("📝 데이터 추출 SQL 쿼리 확인"):
    if selected_option == "3개년 평균":
        st.code("SELECT 광역자치단체명, AVG(방문객수) FROM 지역축제3개년 GROUP BY 광역자치단체명", language='sql')
    else:
        st.code(f"SELECT 광역자치단체명, SUM(방문객수) FROM 지역축제3개년 WHERE 연도 = {year_val} GROUP BY 광역자치단체명", language='sql')