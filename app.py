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

# 2. CSS 최적화
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
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            df.columns = df.columns.str.strip() # 컬럼명 공백 제거
            return df
        except: return None
    return None

df = load_data()

if df is not None:
    # 5. 입력 영역
    c1, c2 = st.columns(2)
    with c1: name_in = st.text_input("강종 검색", placeholder="SPFH590").strip()
    with c2: thick_in = st.text_input("두께(T) 검색", placeholder="1.8").strip()
    
    qty_in = st.number_input("생산 수량(EA) 입력", min_value=0, value=0, step=1000)

    # 6. 필터링 로직
    res = df.copy()
    if name_in: res = res[res['소재명'].astype(str).str.contains(name_in, case=False, na=False)]
    if thick_in:
        try: res = res[res['두께(T)'].astype(float) == float(thick_in)]
        except: pass

    st.divider()

    # 7. 결과 출력 및 선택 로직
    if not res.empty:
        # ✅ 핵심 수정: 제품 단중이 있는 항목만 드롭박스용으로 따로 추출
        calc_ready = res.dropna(subset=['제품 단중']).copy()
        
        st.markdown(f'<div class="search-result-box">✅ 검색 결과: {len(res)}건 (계산 가능: {len(calc_ready)}건)</div>', unsafe_allow_html=True)
        
        if not calc_ready.empty:
            # 폭(W) 정보를 가져오는 함수
            def get_width(row):
                for col in ['폭(W)', '폭', '소재폭', 'WIDTH', 'W']:
                    if col in row.index and pd.notnull(row[col]):
                        return row[col]
                return "-"

            # 드롭다운 라벨 생성
            calc_ready['select_label'] = calc_ready.apply(
                lambda x: f"{x['소재명']} (T:{x.get('두께(T)', '-')} / W:{get_width(x)} / 단중:{x['제품 단중']})", 
                axis=1
            )
            
            selected_label = st.selectbox(
                "계산할 정확한 규격을 선택하세요👇",
                options=calc_ready['select_label'].tolist()
            )
            
            selected_row = calc_ready[calc_ready['select_label'] == selected_label].iloc[0]
            
            # 8. 계산 결과 출력
            if qty_in > 0:
                unit_w = float(selected_row['제품 단중'])
                total_w = unit_w * qty_in
                st.markdown(f"""
                <div class="calc-box">
                    📦 소요량 계산 결과<br>
                    <small>{selected_label.split(' / 단중')[0]}) 기준</small><br>
                    - 적용 단중: {unit_w} kg/EA<br>
                    - 총 구매 필요 중량: {total_w:,.0f} kg
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 검색된 항목 중 단중 데이터가 입력된 규격이 없습니다.")

        # 9. 상세 테이블 (전체 데이터는 여기서 확인 가능)
        with st.expander("📋 전체 규격 리스트 보기 (단중 미입력 포함)"):
            st.table(res.astype(str).replace('nan', '-'))
    else:
        st.warning("검색 결과가 없습니다.")
else:
    st.error("파일 로드 실패")
