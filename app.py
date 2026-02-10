import streamlit as st
import pandas as pd

# 앱 페이지 설정
st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# 디자인 최적화: 전우정밀 스타일 적용
st.markdown("""
    <style>
    /* 상단 회사명 스타일 */
    .company-name {
        font-size: 24px;
        font-weight: bold;
        color: #0047AB; /* 신뢰감을 주는 블루 톤 */
        margin-bottom: -10px;
    }
    .app-title {
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 20px;
    }
    /* 표 디자인 확대 및 중앙 정렬 */
    .stTable { font-size: 20px !important; }
    th { background-color: #f0f2f6 !important; text-align: center !important; }
    td { text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

# 상단 헤더 구성 (회사명 및 로고 텍스트)
st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
st.markdown('<h1 class="app-title">원소재 정보</h1>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # data.xlsx 파일 로드
        df = pd.read_excel("data.xlsx")
        
        # 두께(T)와 폭(W) 반올림 규칙 적용 (소수점 첫째 자리)
        if '두께(T)' in df.columns:
            df['두께(T)'] = pd.to_numeric(df['두께(T)'], errors='coerce').round(1)
        if '폭(W)' in df.columns:
            df['폭(W)'] = pd.to_numeric(df['폭(W)'], errors='coerce').round(1)
            
        return df
    except:
        return None

df = load_data()

if df is not None:
    # 검색 입력창 (맞춤법 교정: 강종명, 두께)
    col1, col2 = st.columns(2)
    with col1:
        name_in = st.text_input("강종명", placeholder="예: SPFH590").strip()
    with col2:
        thick_in = st.text_input("두께(T)", placeholder="예: 1.3").strip()

    # 데이터 필터링 로직
    res = df.copy()
    if name_in:
        res = res[res['소재명'].str.contains(name_in, case=False, na=False)]
    if thick_in:
        try:
            val = float(thick_in)
            res = res[res['두께(T)'] == val]
        except:
            st.warning("숫자 형식을 확인해 주세요.")

    st.divider()

    # 결과 출력 (스크린샷 최적화)
    if not res.empty:
        st.subheader(f"✅ 검색 결과: {len(res)}건")
        st.table(res)
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.info("조건에 일치하는 원소재 정보가 없습니다.")
else:
    st.error("데이터 파일(data.xlsx)을 불러올 수 없습니다.")
