import streamlit as st
import pandas as pd
import os

# 앱 페이지 설정
st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# 디자인 최적화: 전우정밀 전용 스타일
st.markdown("""
    <style>
    .company-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .company-name {
        font-size: 20px;
        font-weight: bold;
        color: #0047AB;
        margin-left: 15px;
    }
    .app-title {
        font-size: 32px;
        font-weight: 800;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    /* 표 디자인 확대 및 가독성 향상 */
    .stTable { font-size: 18px !important; }
    th { background-color: #f0f2f6 !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 상단 로고 및 회사명 배치 ---
col_logo, col_text = st.columns([1, 4])

with col_logo:
    # logo.png 파일이 저장소에 있을 경우 출력
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.info("로고 없음")

with col_text:
    st.markdown('<p class="company-name" style="margin-top:15px;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보</h1>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        # 소수점 반올림 규칙 적용 (1.3000 -> 1.3)
        if '두께(T)' in df.columns:
            df['두께(T)'] = pd.to_numeric(df['두께(T)'], errors='coerce').round(1)
        if '폭(W)' in df.columns:
            df['폭(W)'] = pd.to_numeric(df['폭(W)'], errors='coerce').round(1)
        return df
    except:
        return None

df = load_data()

if df is not None:
    # 검색 입력창 (맞춤법 교정 완료)
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("강종명", placeholder="예: SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T)", placeholder="예: 1.3").strip()

    # 데이터 필터링
    res = df.copy()
    if name_in:
        res = res[res['소재명'].str.contains(name_in, case=False, na=False)]
    if thick_in:
        try:
            val = float(thick_in)
            res = res[res['두께(T)'] == val]
        except:
            st.error("숫자만 입력해 주세요.")

    st.divider()

    # 결과 출력 (스크린샷 최적화 고정형 테이블)
    if not res.empty:
        st.subheader(f"✅ 검색 결과: {len(res)}건")
        # 소수점 표시 형식을 지정하여 깔끔하게 출력
        st.table(res.astype(str)) 
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.info("일치하는 원소재 정보가 없습니다.")
else:
    st.error("data.xlsx 파일을 찾을 수 없습니다.")
