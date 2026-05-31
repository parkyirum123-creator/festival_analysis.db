import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. 페이지 설정 (웹 브라우저 탭에 표시될 이름)
st.set_page_config(page_title="지역축제 방문자 분석", layout="wide")

# --- [초보자 참고] 가상 데이터 생성 함수 (DB가 없을 경우 대비) ---
def init_db():
    conn = sqlite3.connect('축제방문자수.db')
    cursor = conn.cursor()
    
    # 테이블이 없으면 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 지역축제3개년 (
            광역자치단체명 TEXT,
            축제명 TEXT,
            방문객수 INTEGER,
            연도 INTEGER
        )
    ''')
    
    # 데이터가 비어있을 경우에만 Mock Data 삽입
    cursor.execute("SELECT count(*) FROM 지역축제3개년")
    if cursor.fetchone()[0] == 0:
        regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        mock_data = []
        for year in [2023, 2024, 2025]:
            for reg in regions:
                # 수도권/강원/제주는 높게, 나머지는 상대적으로 낮게 설정
                if reg in ['서울', '경기']:
                    base = 8000000 + (year - 2023) * 500000
                elif reg in ['강원', '제주']:
                    base = 5000000 + (year - 2023) * 300000
                else:
                    base = 1500000 + (year - 2023) * 100000
                
                mock_data.append((reg, f"{reg} 대표축제", base, year))
        
        cursor.executemany("INSERT INTO 지역축제3개년 VALUES (?, ?, ?, ?)", mock_data)
        conn.commit()
    conn.close()

# DB 초기화 실행
init_db()

# --- [메인 로직 시작] ---

# 2. 상단 타이틀
st.title("🇰🇷 대한민국 지자체별 연간 축제 총 방문자 수 현황 (3개년)")
st.subheader("지역별 축제 방문자 수 데이터를 한눈에 확인하세요.")

# 3. 사이드바/상단 필터 구성
st.divider()
selected_year = st.selectbox(
    "📊 조회할 연도를 선택해주세요",
    ["2023년", "2024년", "2025년", "3개년 평균"]
)

# 4. 데이터 불러오기 및 쿼리 작성
conn = sqlite3.connect('축제방문자수.db')

# SQL 쿼리 로직
if selected_year == "3개년 평균":
    sql_query = """
    SELECT 광역자치단체명, AVG(total_visitors) as 방문객수
    FROM (
        SELECT 광역자치단체명, 연도, SUM(방문객수) as total_visitors
        FROM 지역축제3개년
        GROUP BY 광역자치단체명, 연도
    )
    GROUP BY 광역자치단체명
    """
else:
    year_val = int(selected_year[:4])
    sql_query = f"""
    SELECT 광역자치단체명, SUM(방문객수) as 방문객수
    FROM 지역축제3개년
    WHERE 연도 = {year_val}
    GROUP BY 광역자치단체명
    """

# 데이터프레임으로 변환
df = pd.read_sql_query(sql_query, conn)
conn.close()

# 5. X축 정렬 순서 고정
fixed_order = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
df['광역자치단체명'] = pd.Categorical(df['광역자치단체명'], categories=fixed_order, ordered=True)
df = df.sort_values('광역자치단체명')

# 6. Plotly 차트 시각화
fig = px.bar(
    df, 
    x='광역자치단체명', 
    y='방문객수',
    title=f"지역별 축제 방문자 수 ({selected_year})",
    labels={'방문객수': '총 방문자 수 (명)', '광역자치단체명': '지역명'},
    text_auto='.2s', # 숫자 단위 자동 축약 표시 (ex: 10M)
    color='방문객수',
    color_continuous_scale='Blues'
)

# 차트 디자인 세밀 조정
fig.update_layout(
    xaxis_title="전국 17개 광역자치단체",
    yaxis_title="방문자 수 (명)",
    title_font_size=20,
    showlegend=False,
    hovermode="x unified"
)

# 차트 출력
st.plotly_chart(fig, use_container_width=True)

# 7. 하단 정보 영역 (SQL 및 인사이트)
st.divider()
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🔍 사용된 SQL 쿼리")
    st.code(sql_query, language='sql')

with col2:
    st.markdown("### 💡 데이터 분석 인사이트")
    st.info(f"""
    1. **수도권 집중 현상**: 서울과 경기 지역의 방문객 수가 타 지역 대비 압도적으로 높습니다. 이는 인프라와 접근성이 반영된 결과입니다.
    2. **관광 특화 지역의 약진**: 강원과 제주는 수도권 제외 지역 중 가장 높은 방문자 수를 기록하며 '관광 강세 지역'임을 입증합니다.
    3. **추세 분석**: {selected_year} 데이터를 통해 지역별 축제 규모와 인구 유입의 상관관계를 파악할 수 있습니다.
    """)

st.caption("Data Source: 공공데이터포털 기반 가상 클린징 데이터 (축제방문자수.db)")