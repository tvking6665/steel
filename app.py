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
with h_col2:
    st.markdown('<p class="company-name" style="margin-top:20px;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보</h1>', unsafe_allow_html=True)

# 데이터 로드 함수 (경로 인식 개선)
@st.cache_data
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            # 숫자 데이터 정리 (272.0 -> 272)
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) and x == int(x) else round(x, 1))
            return df
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            return None
    else:
        return None

df = load_data()

if df is not None:
    # 검색 입력창
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("강종명", placeholder="예: SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T)", placeholder="예: 1.3").strip()

    # 필터링 로직
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
        # 데이터 출력 (소수점 없는 깔끔한 상태 유지)
        st.table(res.astype(str).replace('nan', '-'))
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.info("검색 조건에 맞는 원소재 정보가 없습니다.")
else:
    # 파일이 없을 때 메시지
    st.error("⚠️ 'data.xlsx' 파일을 찾을 수 없습니다. GitHub 저장소에 파일이 있는지 확인해 주세요.")
