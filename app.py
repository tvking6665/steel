import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 및 아이콘(파비콘) 설정
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="전우정밀 원소재 정보 시스템", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# 2. CSS 최적화: 모바일 가독성 및 디자인 설정
st.markdown("""
    <style>
    .main .block-container { padding: 1rem 0.5rem; }
    .company-name { font-size: 16px; font-weight: bold; color: #0047AB; margin-bottom: 2px; }
    .app-title { font-size: 26px; font-weight: 800; margin-top: 0px; margin-bottom: 10px; }
    .stTable { font-size: 12px !important; width: 100% !important; }
    th { background-color: #f8f9fa !important; text-align: center !important; padding: 4px !important; }
    td { text-align: center !important; padding: 4px !important; }
    div[data-testid="stTable"] { overflow-x: auto; }
    </style>
    """, unsafe_allow_html=True)

# 3. 상단 헤더 배치 (버튼 삭제됨)
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=70)
with h_col2:
    st.markdown('<p class="company-name" style="margin-top:10px;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보</h1>', unsafe_allow_html=True)

# 4. 데이터 로드 함수 (숫자 포맷 정리 포함)
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    # 소수점 이하가 0이면 정수로, 아니면 소수점 첫째자리까지 표시
                    df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) and x == int(x) else round(x, 1))
            return df
        except:
            return None
    return None

df = load_data()

if df is not None:
    # 5. 입력 및 설정 영역
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("강종명", placeholder="SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T)", placeholder="1.8").strip()

    # 기타 정보 표시 여부 체크박스 및 도움말
    show_extra = st.checkbox("📋 기타 정보 및 사양 표시", value=True)
    st.caption("💡 **팁**: 화면 캡처 시 표가 잘린다면 체크를 해제해 보세요. 표가 날씬해집니다.")

    # 6. 필터링 로직
    res = df.copy()
    if name_in:
        res = res[res['소재명'].astype(str).str.contains(name_in, case=False, na=False)]
    if thick_in:
        try:
            val = float(thick_in)
            res = res[res['두께(T)'].astype(float) == val]
        except:
            pass

    # 체크박스 상태에 따른 컬럼 제어
    if not show_extra and '기타 정보 및 사양' in res.columns:
        res = res.drop(columns=['기타 정보 및 사양'])

    st.divider()

    # 7. 결과 출력
    if not res.empty:
        st.info(f"✅ 검색 결과: {len(res)}건")
        
        # 순번을 1번부터 다시 매기기
        res_display = res.reset_index(drop=True)
        res_display.index = res_display.index + 1
        
        # 표 출력 (문자열 변환으로 .0 중복 방지)
        st.table(res_display.astype(str).replace('nan', '-'))
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.warning("조건에 맞는 정보가 없습니다.")
else:
    st.error("⚠️ 'data.xlsx' 파일을 불러올 수 없습니다.")
