import streamlit as st
import pandas as pd

st.set_page_config(page_title="소재 규격 검색기", layout="centered")
st.title("🏭 소재 규격 정밀 검색")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        # '두께(T)' 컬럼을 숫자 형식으로 변환 (숫자가 아니면 에러 방지)
        df['두께(T)'] = pd.to_numeric(df['두께(T)'], errors='coerce')
        return df
    except:
        return None

df = load_data()

if df is not None:
    # --- 검색창 디자인 ---
    target_name = st.text_input("🔍 강종명을 입력하세요 (예: SPFH590)").strip()
    
    # 두께 필터 (슬라이더)
    min_t = float(df['두께(T)'].min())
    max_t = float(df['두께(T)'].max())
    t_range = st.slider("📏 두께(T) 범위를 선택하세요", min_t, max_t, (min_t, max_t), step=0.1)

    # --- 필터링 로직 ---
    # 1. 강종명 검색
    filtered_df = df[df['소재명'].str.contains(target_name, case=False, na=False)]
    
    # 2. 선택한 두께 범위 내의 데이터만 추출
    filtered_df = filtered_df[(filtered_df['두께(T)'] >= t_range[0]) & (filtered_df['두께(T)'] <= t_range[1])]

    # --- 결과 출력 ---
    st.divider()
    if not filtered_df.empty:
        st.success(f"검색 결과: {len(filtered_df)}건")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning("조건에 맞는 데이터가 없습니다.")
