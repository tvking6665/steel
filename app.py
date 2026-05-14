import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 및 아이콘 설정
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="전우정밀 원소재 정보 시스템", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="전우정밀 원소재 정보 시스템", layout="centered")

# 2. CSS 최적화 (디자인 및 시인성)
st.markdown("""
<style>
    .main .block-container { padding: 1rem 0.5rem; }
    .company-name { font-size: 16px; font-weight: bold; color: #0047AB; margin-bottom: 2px; }
    .app-title { font-size: 26px; font-weight: 800; margin-top: 0px; margin-bottom: 10px; }
    .stTable { font-size: 12px !important; width: 100% !important; }
    th { background-color: #f8f9fa !important; text-align: center !important; padding: 4px !important; color: black !important; }
    td { text-align: center !important; padding: 4px !important; }
    
    .mes-button {
        display: inline-block;
        padding: 0.5em 1em;
        color: white !important;
        background-color: #E60012;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 15px;
        text-align: center;
    }

    /* 검색 결과 박스 */
    .search-result-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 2px solid #1c83e1;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 15px 0px;
        color: #58a6ff !important;
        font-weight: bold;
        font-size: 18px;
    }
    
    /* 소요량 계산 결과 박스 */
    .calc-box {
        background-color: rgba(40, 167, 69, 0.1);
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0px;
        color: #72ff8d !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 3. 상단 헤더
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=70)
with h_col2:
    st.markdown('<p class="company-name" style="margin-top:10px;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
    st.markdown('<a href="http://mes.jwjm.com/bang.asp" target="_blank" class="mes-button">📊 실시간 가동 현황판 보기</a>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보 및 소요량 계산</h1>', unsafe_allow_html=True)

# 4. 데이터 로드 함수
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            return df
        except: return None
    return None

df = load_data()

if df is not None:
    # 5. 입력 영역
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        name_in = st.text_input("강종명", placeholder="SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T)", placeholder="1.8").strip()
    with c3:
        # 생산 수량 입력
        qty_in = st.number_input("생산 수량(EA)", min_value=0, value=0, step=100)

    show_extra = st.checkbox("📋 기타 정보 및 사양 표시", value=True)

    # 6. 필터링 로직
    res = df.copy()
    if name_in:
        res = res[res['소재명'].astype(str).str.contains(name_in, case=False, na=False)]
    if thick_in:
        try:
            val = float(thick_in)
            res = res[res['두께(T)'].astype(float) == val]
        except: pass

    st.divider()

    # 7. 결과 및 계산 출력
    if not res.empty:
        # 검색 결과 건수 표시
        st.markdown(f'<div class="search-result-box">✅ 검색 결과: {len(res)}건</div>', unsafe_allow_html=True)
        
        # 수량이 입력된 경우 소요량 계산 박스 노출
        if qty_in > 0:
            try:
                # 첫 번째 검색 결과의 단중 기준
                unit_weight = float(res['제품 단중'].iloc[0])
                total_weight = unit_weight * qty_in
                
                # 소수점 없이 정수로 표시 (:.0f)
                st.markdown(f"""
                <div class="calc-box">
                    💡 예상 소요량 요약 (첫 번째 항목 기준)<br>
                    - 선택 단중: {unit_weight} kg/EA<br>
                    - 목표 수량: {qty_in:,} EA<br>
                    - 📦 총 구매 필요 중량: {total_weight:,.0f} kg
                </div>
                """, unsafe_allow_html=True)
            except:
                st.warning("단중 데이터가 비어있거나 숫자가 아니어서 계산할 수 없습니다.")

        # 데이터 테이블 출력
        res_display = res.copy()
        if not show_extra and '기타 정보 및 사양' in res_display.columns:
            res_display = res_display.drop(columns=['기타 정보 및 사양'])
            
        res_display = res_display.reset_index(drop=True)
        res_display.index = res_display.index + 1
        st.table(res_display.astype(str).replace('nan', '-'))
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.warning("조건에 맞는 정보가 없습니다.")
else:
    st.error("⚠️ 'data.xlsx' 파일을 불러올 수 없습니다.")
