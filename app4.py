import streamlit as st
import pandas as pd
import sqlite3
import os

# 1. 페이지 설정
st.set_page_config(page_title="공공데이터 축제 분석", layout="wide")

# 2. 데이터 불러오기 함수
def load_data():
    db_name = 'organization.db'
    
    # 파일이 있는지 먼저 확인해서 에러를 방지합니다.
    if not os.path.exists(db_name):
        st.error(f"'{db_name}' 파일을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요.")
        return None

    conn = sqlite3.connect(db_name)
    
    # 두 테이블을 하나로 합치는 SQL 쿼리 (UNION ALL 사용)
    # 2025년 테이블과 2026년 테이블의 데이터를 모두 가져옵니다.
    query = """
    SELECT 연도, 조직형태, 축제수 FROM festival_org_detailed_2025
    UNION ALL
    SELECT 연도, 조직형태, 축제수 FROM festival_org_detailed_2026
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"데이터를 읽어오는 중 오류 발생: {e}")
        return None
    finally:
        conn.close()

# --- 화면 구성 시작 ---
st.title("📊 2025-2026 조직형태별 축제수 비교")
st.markdown("두 개의 테이블(`2025`, `2026`) 데이터를 합쳐서 비교 분석합니다.")

df = load_data()

if df is not None:
    # 3. 차트를 위한 데이터 가공 (Pivoting)
    # st.bar_chart는 '인덱스'가 X축 이름이 되고, '컬럼'이 막대가 됩니다.
    # 우리는 '조직형태'를 옆으로 나열하고, '연도'별로 막대를 세울 거예요.
    chart_data = df.pivot(index='조직형태', columns='연도', values='축제수')

    # 4. 차트 출력 (이중 막대 차트)
    st.subheader("조직형태별 축제수 이중 막대 차트")
    st.bar_chart(chart_data, stack=False)

    # 5. 데이터 표 출력 (선택 사항)
    with st.expander("상세 데이터 보기"):
        st.write("표 형식 데이터:")
        st.dataframe(chart_data, use_container_width=True)
