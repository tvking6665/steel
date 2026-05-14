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

# 2. CSS 최적화 (다크모드 시인성 및 버튼 디자인)
st.markdown("""
<style>
    .main .block-container { padding: 1rem 0.5rem; }
    .company-name { font-size: 16px; font-weight: bold; color: #0047AB; margin-bottom: 2px; }
    .app-title { font-size: 26px; font-weight: 800; margin-top: 0px; margin-bottom: 10px; }
    
    /* 실시간 가동 현황판 버튼 */
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

    /* 검색 결과 안내 박스 */
    .search-result-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 2px solid #1c83e1;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 10px 0px;
        color: #58a6ff !important;
        font-weight: bold;
    }
    
    /* ✅ 코일 소요량 계산 결과 박스 */
    .calc-box {
        background-color: rgba(40, 167, 69, 0.1);
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0px;
        color: #72ff8d !important;
        font-weight: bold;
    }

    /* 테이블 스타일 조정 */
    .stTable { font-size: 12px !important; }
    th { background-color: #f8f9fa !important; color: black !important; text-align: center !important; }
    td { text-align: center !important; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 헤더 및 로고 배치
h_col1, h_col2 = st.columns([1, 4])
with h_col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=70)
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
            return pd.read_excel(file_name, engine='openpyxl')
        except:
            return None
    return None

df = load_data()

if df is not None:
    # 5. 입력 영역 (강종명, 두께, 생산수량)
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        name_in = st.text_input("강종명 검색", placeholder="SPFH590").strip()
    with c2:
        thick_in = st.text_input("두께(T) 검색", placeholder="1.8").strip()
    with c3:
        qty_in = st.number_input("생산 수량(EA) 입력", min_value=0, value=0, step=100)

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

    st.divider()

    # 7. 결과 출력 및 소재 선택 (라디오 버튼)
    if not res.empty:
        st.markdown(f'<div class="search-result-box">✅ 검색 결과: {len(res)}건 (계산할 항목을 선택하세요)</div>', unsafe_allow_html=True)
        
        # 선택용 목록 생성 (소재명 + 두께 + 단중 정보를 합쳐서 보여줌)
        res['display_name'] = res.apply(lambda x: f"{x['소재명']} (T:{x['두께(T)']} / 단중:{x['제품 단중']})", axis=1)
        
        # 라디오 버튼으로 직접 선택
        selected_option = st.radio(
            "계산할 소재 선택:",
            options=res['display_name'].tolist(),
            label_visibility="visible"
        )
        
        # 선택된 행 데이터 가져오기
        selected_row = res[res['display_name'] == selected_option].iloc[0]
        
        # 8. 계산 박스 출력 (수량이 0보다 클 때만)
        if qty_in > 0:
            try:
                unit_weight = float(selected_row['제품 단중'])
                total_weight = unit_weight * qty_in
                
                st.markdown(f"""
                <div class="calc-box">
                    🎯 선택된 소재: {selected_row['소재명']} (T:{selected_row['두께(T)']})<br>
                    - 적용 단중: {unit_weight} kg/EA<br>
                    - 목표 수량: {qty_in:,} EA<br>
                    - 📦 총 구매 필요 중량: {total_weight:,.0f} kg
                </div>
                """, unsafe_allow_html=True)
            except:
                st.warning("선택한 항목의 단중 데이터에 오류가 있습니다.")

        # 9. 상세 규격 테이블 (표)
        st.write("📋 상세 규격 데이터")
        # 선택용 임시 컬럼은 제외하고 출력
        st.table(res.drop(columns=['display_name']).astype(str).replace('nan', '-'))
        st.caption("© Jeon Woo Precision Co., LTD. All rights reserved.")
    else:
        st.warning("조건에 맞는 원소재 정보가 없습니다.")
else:
    st.error("⚠️ 'data.xlsx' 파일을 불러올 수 없습니다. 파일명과 위치를 확인하세요.")
