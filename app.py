import streamlit as st
import pandas as pd

st.set_page_config(page_title="강종 검색기", layout="centered")
st.title("🏭 소재 규격 간편 검색")

@st.cache_data
def load_data():
    try:
        return pd.read_excel("data.xlsx")
    except:
        return None

df = load_data()

if df is not None:
    target_name = st.text_input("🔍 강종명을 입력하세요 (예: SPFC590)").strip()
    if target_name:
        result = df[df['소재명'].str.contains(target_name, case=False, na=False)]
        if not result.empty:
            st.success(f"검색 결과: {len(result)}건")
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.warning("일치하는 강종명이 없습니다.")