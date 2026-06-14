import streamlit as st

# 1. 전체 화면을 넓게 쓰기 위한 설정
st.set_page_config(layout="wide")

st.title("🏆 축제 데이터 분석 최종 대시보드")
st.write("6명의 팀원이 분석한 시각화 화면을 한눈에 보여줍니다.")
st.divider() # 구분선

# ==========================================
# 1번부터 6번 팀원 파일 차례대로 실행하기
# ==========================================

try:
    st.header("📊 섹션 1")
    with open("app1.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"1번 화면을 불러오는 중 에러 발생: {e}")

st.divider()

try:
    st.header("📊 섹션 2")
    with open("app2.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"2번 화면을 불러오는 중 에러 발생: {e}")

st.divider()

try:
    st.header("📊 섹션 3")
    with open("app3.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"3번 화면을 불러오는 중 에러 발생: {e}")

st.divider()

try:
    st.header("📊 섹션 4")
    with open("app4.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"4번 화면을 불러오는 중 에러 발생: {e}")

st.divider()

try:
    st.header("📊 섹션 5")
    with open("app5.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"5번 화면을 불러오는 중 에러 발생: {e}")

st.divider()

try:
    st.header("📊 섹션 6")
    with open("app6.py", encoding="utf-8") as f:
        exec(f.read())
except Exception as e:
    st.error(f"6번 화면을 불러오는 중 에러 발생: {e}")