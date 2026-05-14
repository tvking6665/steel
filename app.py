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

# 2. CSS 최적화 (모바일 시인성 및 '적용' 버튼 강조)
st.markdown("""
<style>
    .main .block-container { padding: 1rem 0.5rem; }
    .company-name { font-size: 14px; font-weight: bold; color: #0047AB; margin-bottom: 2px; }
    .app-title { font-size: 22px; font-weight: 800; margin-top: 0px; margin-bottom: 10px; }
    
    /* '적용' 버튼 스타일: 모바일에서 터치하기 쉽게 크게 설정 */
    div.stButton > button:first-child {
        width: 100%;
        background-color: #1c83e1;
        color: white;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
        border: none;
    }
    
    .search-result-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1.5px solid #1c83e1;
        padding: 10px;
        border-radius: 8px;
        color: #58a6ff !important;
        font-weight: bold;
        margin-top: 10px;
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
    st.markdown('<a href="http://mes.jwjm.com/bang.asp" target="_blank" style="text-decoration:none; font-size:12px; color:#E60012; font-weight:bold;">📊 실시간 가동 현황판</a>', unsafe_allow_html=True)

st.markdown('<h1 class="app-title">원소재 정보 조회 및 적용</h1>', unsafe_allow_html=True)

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
    # --- 5. 입력 양식 (st.form 사용으로 모바일 터치 오작동 방지) ---
    with st.form("search_form"):
        st.write("🔍 **찾으시는 소재 정보를 입력하세요**")
        c1, c2 = st.columns(2)
        with c1:
            # 한글화 하실 것을 대비해 유연하게 설정
            name_in = st.text_input("강종명", placeholder="SPFH590").strip()
        with c2:
            thick_in = st.text_input("두께", placeholder="1.8").strip()
        
        qty_in = st.number_input("생산 예정 수량 (EA)", min_value=0, value=0, step=1000)
        
        # ✅ '적용 및 조회' 버튼
        submit_button = st.form_submit_button("✅ 설정 내용 적용")

    # --- 6. 결과 출력 (버튼 클릭 시에만 실행) ---
    if submit_button:
        res = df.copy()
        
        # 강종 필터
        if name_in:
            res = res[res['소재명'].astype(str).str.contains(name_in, case=False, na=False)]
        
        # 두께 필터 (두께(T) 또는 두께 컬럼 대응)
        if thick_in:
            t_col = '두께(T)' if '두께(T)' in res.columns else '두께'
            try:
                res = res[res[t_col].astype(float) == float(thick_in)]
            except: pass

        if not res.empty:
            # 제품 단중이 있는 항목만 드롭다운에 노출
            calc_ready = res.dropna(subset=['제품 단중']).copy()
            
            st.markdown(f'<div class="search-result-box">✅ 조회 결과: {len(res)}건</div>', unsafe_allow_html=True)
            
            if not calc_ready.empty:
                # 폭(W) 정보 탐색
                def get_w(row):
                    for c in ['폭', '폭(W)', '소재폭', 'WIDTH', 'W']:
                        if c in row.index and pd.notnull(row[c]): return row[c]
                    return "-"

                # 두께 정보 탐색
                def get_t(row):
                    for c in ['두께', '두께(T)', 'T']:
                        if c in row.index and pd.notnull(row[c]): return row[c]
                    return "-"

                calc_ready['label'] = calc_ready.apply(
                    lambda x: f"{x['소재명']} (두께:{get_t(x)} / 폭:{get_w(x)} / 단중:{x['제품 단중']})", axis=1
                )
                
                # 규격 선택
                selected_label = st.selectbox("상세 규격 선택", options=calc_ready['label'].tolist())
                selected_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]
                
                # 수량이 입력된 경우에만 소요량 계산 결과 표시
                if qty_in > 0:
                    unit_w = float(selected_row['제품 단중'])
                    total_w = unit_w * qty_in
                    st.markdown(f"""
                    <div class="calc-box">
                        📋 적용 결과 요약<br>
                        - 선택 규격: {selected_row['소재명']}<br>
                        - 적용 단중: {unit_w} kg/EA<br>
                        - 📦 총 소요 예정량: {total_w:,.0f} kg
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("💡 생산 수량을 입력하시면 소요 중량이 자동 계산됩니다.")
            else:
                st.warning("조회된 항목 중 단중 정보가 입력된 규격이 없습니다.")
        else:
            st.warning("조건에 맞는 정보가 없습니다. 검색어를 확인해 주세요.")

    # 상세 데이터 expander
    with st.expander("📊 전체 원소재 데이터베이스 확인"):
        st.table(df.astype(str).replace('nan', '-'))

else:
    st.error("데이터 파일을 찾을 수 없습니다. 'data.xlsx' 파일을 확인해 주세요.")
