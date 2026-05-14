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
    
    div.stButton > button:first-child {
        width: 100%;
        background-color: #1c83e1;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        margin-top: 10px;
    }
    
    .search-result-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1.5px solid #1c83e1;
        padding: 10px;
        border-radius: 8px;
        color: #58a6ff !important;
        font-weight: bold;
        margin: 10px 0px;
    }
    .calc-box {
        background-color: rgba(40, 167, 69, 0.15);
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        color: #72ff8d !important;
        font-weight: bold;
        font-size: 16px;
        margin-top: 15px;
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

st.markdown('<h1 class="app-title">원소재 정보 시스템</h1>', unsafe_allow_html=True)

# 4. 데이터 로드
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            df.columns = df.columns.str.strip()
            return df
        except: return None
    return None

df = load_data()

# 정보 추출용 헬퍼 함수
def get_val(row, cols):
    for c in cols:
        if c in row.index and pd.notnull(row[c]): return row[c]
    return "-"

if df is not None:
    # 5. 입력 영역
    st.write("🔍 **소재 검색 및 수량 입력**")
    c1, c2 = st.columns(2)
    with c1:
        name_in = st.text_input("강종명", placeholder="전체 검색 시 공백").strip()
    with c2:
        thick_in = st.text_input("두께", placeholder="예: 1.8").strip()
    
    qty_in = st.number_input("생산 예정 수량 (EA)", min_value=0, value=0, step=1000)

    # 필터링 로직
    res = df.copy()
    if name_in:
        res = res[res['소재명'].astype(str).str.contains(name_in, case=False, na=False)]
    if thick_in:
        t_col = '두께(T)' if '두께(T)' in res.columns else '두께'
        try: res = res[res[t_col].astype(float) == float(thick_in)]
        except: pass

    st.divider()

    # 6. 결과 출력
    if not res.empty:
        calc_ready = res.dropna(subset=['제품 단중']).copy()
        st.markdown(f'<div class="search-result-box">✅ 조회 결과: {len(res)}건</div>', unsafe_allow_html=True)
        
        if not calc_ready.empty:
            calc_ready['label'] = calc_ready.apply(
                lambda x: f"{x['소재명']} (T:{get_val(x, ['두께','두께(T)','T'])} / W:{get_val(x, ['폭','폭(W)','W','소재폭'])} / 단중:{x['제품 단중']})", axis=1
            )
            
            selected_label = st.selectbox("🎯 정확한 상세 규격 선택", options=calc_ready['label'].tolist())
            selected_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]
            
            # 7. 적용 버튼 및 소요량 계산
            if st.button("✅ 설정 내용 적용"):
                if qty_in > 0:
                    unit_w = float(selected_row['제품 단중'])
                    total_kg = unit_w * qty_in
                    total_ton = total_kg / 1000
                    
                    final_t = get_val(selected_row, ['두께','두께(T)','T'])
                    final_w = get_val(selected_row, ['폭','폭(W)','W','소재폭'])
                    
                    # ✅ 요약 박스 문구 업데이트
                    st.markdown(f"""
                    <div class="calc-box">
                        📋 최종 적용 요약<br>
                        - 규격: {selected_row['소재명']}<br>
                        - 두께(T): {final_t} / 폭(W): {final_w}<br>
                        - 단중: {unit_w} kg<br>
                        - 구매 예정수량: {qty_in:,} EA<br>
                        - 📦 총 구매 예정량: {total_kg:,.0f} kg ({total_ton:,.1f} ton)
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("생산 수량을 입력해야 소요량이 계산됩니다.")
        else:
            st.info("💡 단중 정보가 있는 규격이 없습니다.")

        with st.expander("📊 상세 데이터 시트 확인"):
            st.table(res.astype(str).replace('nan', '-'))
    else:
        st.warning("검색 조건에 맞는 데이터가 없습니다.")
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
