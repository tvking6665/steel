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

# 2. CSS 최적화 (모바일 시인성 및 결과 박스 강조)
st.markdown("""
<style>
    .main .block-container { padding: 1rem 0.5rem; }
    .company-name { font-size: 14px; font-weight: bold; color: #0047AB; margin-bottom: 2px; }
    .app-title { font-size: 22px; font-weight: 800; margin-top: 0px; margin-bottom: 10px; }
    
    .mes-button {
        display: inline-block;
        padding: 0.4em 0.8em;
        color: white !important;
        background-color: #E60012;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        font-size: 13px;
        margin-bottom: 10px;
    }
    .search-result-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1.5px solid #1c83e1;
        padding: 10px;
        border-radius: 8px;
        color: #58a6ff !important;
        font-weight: bold;
        font-size: 15px;
        margin-bottom: 10px;
    }
    .calc-box {
        background-color: rgba(40, 167, 69, 0.15);
        border: 2px solid #28a745;
        padding: 12px;
        border-radius: 8px;
        color: #72ff8d !important;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
    }
    .stTable { font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# 3. 상단 헤더
h_col1, h_col2 = st.columns([1, 3])
with h_col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=60)
with h_col2:
    st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
    st.markdown('<a href="http://mes.jwjm.com/bang.asp" target="_blank" class="mes-button">📊 현황판 보기</a>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보 시스템</h1>', unsafe_allow_html=True)

# 4. 데이터 로드
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try: return pd.read_excel(file_name, engine='openpyxl')
        except: return None
    return None

df = load_data()

if df is not None:
    # 5. 입력 영역
    c1, c2 = st.columns(2)
    with c1: name_in = st.text_input("강종 검색", placeholder="SPFH590").strip()
    with c2: thick_in = st.text_input("두께(T) 검색", placeholder="1.8").strip()
    
    qty_in = st.number_input("생산 수량(EA) 입력", min_value=0, value=0, step=1000)

    # 6. 필터링
    res = df.copy()
    if name_in: res = res[res['소재명'].astype(str).str.contains(name_in, case=False, na=False)]
    if thick_in:
        try: res = res[res['두께(T)'].astype(float) == float(thick_in)]
        except: pass

    st.divider()

    # 7. 결과 출력 및 선택 (폭 정보 추가)
    if not res.empty:
        st.markdown(f'<div class="search-result-box">✅ 검색 결과: {len(res)}건</div>', unsafe_allow_html=True)
        
        # 💡 선택 목록에 '폭' 정보 추가
        # 엑셀의 컬럼명이 '폭' 또는 '소재폭' 등 실제 이름과 맞는지 확인이 필요합니다.
        # 여기서는 보편적인 '폭'으로 설정했습니다.
        def create_label(row):
            width = row.get('폭', row.get('소재폭', '-'))
            return f"{row['소재명']} (T:{row['두께(T)']} / W:{width} / 단중:{row['제품 단중']})"
        
        res['select_label'] = res.apply(create_label, axis=1)
        
        selected_label = st.selectbox(
            "계산할 정확한 규격을 선택하세요👇",
            options=res['select_label'].tolist()
        )
        
        selected_row = res[res['select_label'] == selected_label].iloc[0]
        
        # 8. 계산 결과 출력
        if qty_in > 0:
            try:
                unit_w = float(selected_row['제품 단중'])
                total_w = unit_w * qty_in
                st.markdown(f"""
                <div class="calc-box">
                    📦 소요량 계산 결과<br>
                    <small>{selected_label.split(' / 단중')[0]}) 기준</small><br>
                    - 적용 단중: {unit_w} kg/EA<br>
                    - 총 구매 필요 중량: {total_weight:,.0f} kg
                </div>
                """, unsafe_allow_html=True)
            except:
                st.warning("단중 데이터 확인 필요")

        # 9. 상세 테이블 (숨김 처리)
        with st.expander("📋 전체 상세 데이터 확인"):
            st.table(res.drop(columns=['select_label']).astype(str).replace('nan', '-'))
    else:
        st.warning("검색 결과가 없습니다.")
else:
    st.error("파일 로드 실패")
