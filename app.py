import streamlit as st
import pandas as pd
import os

# 앱 페이지 설정
st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# 디자인 최적화
st.markdown("""
    <style>
    .company-name { font-size: 20px; font-weight: bold; color: #0047AB; margin-bottom: 5px; }
    .app-title { font-size: 32px; font-weight: 800; margin-top: -10px; margin-bottom: 20px; }
    .stTable { font-size: 18px !important; width: 100% !important; }
    th { background-color: #f8f9fa !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# 상단 로고 및 회사명 배치
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
with h_col2:
    st.markdown('<p class="company-name" style="margin-top:20px;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보</h1>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            # 숫자 데이터 정리 (소수점이 0이면 제거)
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) and x == int(x) else round(x, 1))
            return df
        except:
            return None
    return None

df = load_data()

if df is not None:
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("강종명", placeholder="예: SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T)", placeholder="예: 1.3").strip()

    res = df.copy()
    if name_in:
        res = res[res['소재명'].str.contains(name_in, case=False, na=False)]
    if thick_in:
        try:
            val = float(thick_in)
            res = res[res['두께(T)'].astype(float) == val]
        except:
            pass

    st.divider()

    if not res.empty:
        st.subheader(f"✅ 검색 결과: {len(res)}건")
        
        # --- 핵심 수정 부분: 순서를 1부터 다시 매기기 ---
        res_display = res.reset_index(drop=True) # 기존 인덱스 제거
        res_display.index = res_display.index + 1 # 1부터 시작하도록 설정
        
        # 표 출력
        st.table(res_display.astype(str).replace('nan', '-'))
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.info("검색 조건에 맞는 원소재 정보가 없습니다.")
else:
    st.error("⚠️ 'data.xlsx' 파일을 찾을 수 없습니다.")
