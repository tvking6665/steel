import streamlit as st
import pandas as pd
import os

# 앱 페이지 설정
st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# 디자인 최적화: 전우정밀 전용 스타일
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
    else:
        st.write("⚠️ 로고 확인")
with h_col2:
    st.markdown('<p class="company-name" style="margin-top:20px;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보</h1>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        # 숫자 데이터를 깔끔하게 정리 (272.0 -> 272, 1.300 -> 1.3)
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # 소수점 이하가 0이면 정수로, 아니면 소수점 첫째자리까지
                df[col] = df[col].apply(lambda x: int(x) if x == int(x) else round(x, 1))
        return df
    except:
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
            # 입력값과 비교할 때도 유연하게 처리
            res = res[res['두께(T)'].astype(float) == val]
        except:
            st.error("숫자만 입력해 주세요.")

    st.divider()

    if not res.empty:
        st.subheader(f"✅ 검색 결과: {len(res)}건")
        # 데이터를 문자열로 변환하여 .0 방지
        st.table(res.astype(str))
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.info("조건에 일치하는 정보가 없습니다.")
else:
    st.error("data.xlsx 파일을 찾을 수 없습니다.")
