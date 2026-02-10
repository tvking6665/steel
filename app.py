import streamlit as st
import pandas as pd

st.set_page_config(page_title="소재 규격 검색기", layout="centered")
st.title("🏭 소재 규격 정밀 검색")

@st.cache_data
def load_data():
    try:
        # 엑셀 파일 로드 (파일명 확인 필수)
        df = pd.read_excel("data.xlsx")
        # '두께(T)' 컬럼을 숫자형으로 변환하여 검색 정확도 높임
        df['두께(T)'] = pd.to_numeric(df['두께(T)'], errors='coerce')
        return df
    except:
        return None

df = load_data()

if df is not None:
    # --- 입력창 구성 (강종명과 두께를 나란히 또는 위아래로 배치) ---
    st.subheader("🔍 검색 조건을 입력하세요")
    
    target_name = st.text_input("1️⃣ 강종명 (예: SPFH590)").strip()
    
    # 두께 입력창: 숫자만 입력 가능하도록 설정 (value=0.0은 초기값)
    target_t = st.text_input("2️⃣ 두께(T) 입력 (예: 1.8)").strip()

    # --- 필터링 로직 ---
    # 기본 데이터 복사
    filtered_df = df.copy()

    # 1. 강종명 필터링 (입력값이 있을 때만 실행)
    if target_name:
        filtered_df = filtered_df[filtered_df['소재명'].str.contains(target_name, case=False, na=False)]
    
    # 2. 두께 필터링 (입력값이 있을 때만 실행)
    if target_t:
        try:
            t_value = float(target_t)
            filtered_df = filtered_df[filtered_df['두께(T)'] == t_value]
        except ValueError:
            st.error("두께는 숫자만 입력해 주세요. (예: 1.8)")

    # --- 결과 출력 ---
    st.divider()
    if not filtered_df.empty:
        st.success(f"검색 결과: {len(filtered_df)}건")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning("일치하는 소재 데이터가 없습니다. 입력값을 확인해 주세요.")
else:
    st.error("데이터 파일(data.xlsx)을 찾을 수 없습니다.")
