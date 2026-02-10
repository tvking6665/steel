import streamlit as st
import pandas as pd
import os

# 앱 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# CSS 최적화: 모바일 가독성 향상
st.markdown("""
    <style>
    .main .block-container { padding: 1rem 1rem; }
    .company-name { font-size: 18px; font-weight: bold; color: #0047AB; margin-bottom: 5px; }
    .app-title { font-size: 28px; font-weight: 800; margin-top: -5px; margin-bottom: 15px; }
    .stTable { font-size: 14px !important; width: 100% !important; }
    th { background-color: #f8f9fa !important; text-align: center !important; padding: 5px !important; }
    td { text-align: center !important; padding: 5px !important; }
    div[data-testid="stTable"] { overflow-x: auto; }
    </style>
    """, unsafe_allow_html=True)

# 상단 로고 및 회사명 배치
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
with h_col2:
    st.markdown('<p class="company-name" style="margin-top:10px;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보</h1>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            # 숫자 데이터 깔끔하게 정리 (272.0 -> 272)
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) and x == int(x) else round(x, 1))
            return df
        except:
            return None
    return None

df = load_data()

if df is not None:
    # 1. 입력창 배치
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("강종명", placeholder="SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T)", placeholder="1.8").strip()

    # 2. 기타 정보 표시 여부 체크박스 (기본값은 표시)
    show_extra = st.checkbox("📋 기타 정보 및 사양 표시", value=True)

    res = df.copy()
    if name_in:
        res = res[res['소재명'].str.contains(name_in, case=False, na=False)]
    if thick_in:
        try:
            val = float(thick_in)
            res = res[res['두께(T)'].astype(float) == val]
        except:
            pass

    # 체크박스가 해제되어 있으면 '기타 정보 및 사양' 컬럼 제거
    if not show_extra and '기타 정보 및 사양' in res.columns:
        res = res.drop(columns=['기타 정보 및 사양'])

    st.divider()

    if not res.empty:
        st.info(f"✅ 검색 결과: {len(res)}건")
        
        # 순번 1부터 재설정
        res_display = res.reset_index(drop=True)
        res_display.index = res_display.index + 1
        
        # 표 출력
        st.table(res_display.astype(
