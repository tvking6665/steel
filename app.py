import streamlit as st
import pandas as pd

st.set_page_config(page_title="강종 및 두께 검색기", layout="centered")
st.title("🏭 소재 규격 정밀 검색")

@st.cache_data
def load_data():
    try:
        # 엑셀 파일 읽기 (파일명이 data.xlsx인지 확인하세요)
        df = pd.read_excel("data.xlsx")
        # 검색을 위해 두께 컬럼을 숫자형으로 변환 (컬럼명이 '두께'라고 가정)
        df['두께'] = pd.to_numeric(df['두께'], errors='coerce')
        return df
    except:
        return None

df = load_data()

if df is not None:
    # --- 사이드바 또는 상단에 검색 조건 배치 ---
    st.subheader("🔍 검색 조건 설정")
    
    col1, col2 = st.columns(2)
    with col1:
        target_name = st.text_input("강종명 입력 (예: SPFC590)").strip()
    
    with col2:
        # 엑셀의 두께 데이터를 바탕으로 슬라이더 범위 설정
        min_t = float(df['두께'].min())
        max_t = float(df['두께'].max())
        t_range = st.slider("두께(T) 범위 선택", min_t, max_t, (min_t, max_t), step=0.1)

    # --- 필터링 로직 ---
    # 1. 강종명 필터링
    filtered_df = df[df['소재명'].str.contains(target_name, case=False, na=False)]
    
    # 2. 두께 범위 필터링
    filtered_df = filtered_df[(filtered_df['두께'] >= t_range[0]) & (filtered_df['두께'] <= t_range[1])]

    # --- 결과 출력 ---
    st.divider()
    if not filtered_df.empty:
        st.success(f"검색 결과: {len(filtered_df)}건")
        # 표 형식으로 출력
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning("조건에 일치하는 소재가 없습니다. 검색어를 확인하거나 두께 범위를 조절해 보세요.")
else:
    st.error("데이터 파일(data.xlsx)을 불러올 수 없습니다. 파일명과 위치를 확인해 주세요.")
