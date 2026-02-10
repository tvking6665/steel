import streamlit as st
import pandas as pd
import os

# 앱 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# CSS 최적화: 모바일에서 표가 잘리지 않도록 여백 및 글자 크기 조정
st.markdown("""
    <style>
    /* 전체 여백 감소 */
    .main .block-container { padding: 1rem 1rem; }
    
    /* 회사명 및 제목 스타일 */
    .company-name { font-size: 18px; font-weight: bold; color: #0047AB; margin-bottom: 5px; }
    .app-title { font-size: 28px; font-weight: 800; margin-top: -5px; margin-bottom: 15px; }
    
    /* 표 스타일: 모바일 화면에 맞춰 글자 크기 및 여백 최소화 */
    .stTable { font-size: 14px !important; width: 100% !important; }
    th { background-color: #f8f9fa !important; text-align: center !important; padding: 5px !important; }
    td { text-align: center !important; padding: 5px !important; }
    
    /* 가로 스크롤 허용 설정 */
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
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) and x == int(x) else round(x, 1))
            return df
        except:
            return None
    return None

df = load_data()

if df is not None:
    # 입력창 가로 배치 (공간 절약)
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("강종명", placeholder="SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T)", placeholder="1.8").strip()

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
        st.info(f"✅ 검색 결과: {len(res)}건")
        
        # 순번을 1부터 다시 매기고 인덱스 열 이름 설정
        res_display = res.reset_index(drop=True)
        res_display.index = res_display.index + 1
        
        # 표 출력 (문자열 변환으로 .0 방지)
        st.table(res_display.astype(str).replace('nan', '-'))
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.warning("일치하는 정보가 없습니다.")
else:
    st.error("⚠️ 'data.xlsx' 파일을 찾을 수 없습니다.")
