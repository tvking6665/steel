import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 설정
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="전우정밀 시스템", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="전우정밀 시스템", page_icon="📊", layout="centered")

# 2. [핵심] 5:5 배치를 위한 강제 스타일 시트
st.markdown("""
<style>
    /* 전체 여백 최소화 */
    .main .block-container { padding: 0.5rem 0.5rem; }
    
    /* 컬럼 간격 강제 조정 (모바일에서 가로 배치 유지) */
    [data-testid="column"] {
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }
    
    /* 입력창 라벨 크기 및 간격 축소 */
    label { font-size: 13px !important; font-weight: bold !important; margin-bottom: -15px !important; }
    .stNumberInput, .stSelectbox { margin-bottom: -10px !important; }
    
    /* 회사 로고 및 타이틀 정렬 */
    .title-text { font-size: 18px !important; font-weight: 800; text-align: center; margin-top: -10px; color: #1E3A8A; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            df.columns = df.columns.str.strip()
            df.rename(columns={'소재명': '강종명', '두께(T)': '두께', '폭(W)': '폭', '제품 단중': '단중', '기타정보및사양': '프로젝트명'}, inplace=True, errors='ignore')
            if '단중' in df.columns: df['단중'] = pd.to_numeric(df['단중'], errors='coerce')
            return df
        except: return None
    return None

df_raw = load_data()

# 4. 로그인 (생략 가능하면 삭제 가능)
if "auth_success" not in st.session_state: st.session_state.auth_success = False
if not st.session_state.auth_success:
    if os.path.exists("logo.png"): st.image("logo.png", width=100)
    st.markdown('<p class="title-text">RAW MATERIAL SYSTEM</p>', unsafe_allow_html=True)
    user = st.selectbox("사용자", ["선택하세요", "관리자"])
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인", use_container_width=True):
        if pw == "1128": st.session_state.auth_success = True; st.rerun()
    st.stop()

# 5. 메인 레이아웃 (5:5 배치)
if 'v' not in st.session_state: st.session_state.v = 0
v = st.session_state.v

# 상단 로고
if os.path.exists("logo.png"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m: st.image("logo.png", use_container_width=True)
st.markdown('<p class="title-text">RAW MATERIAL INFORMATION</p>', unsafe_allow_html=True)

# [5:5 배치 구간 1]
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{v}")
with row1_col2:
    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{v}")

# [5:5 배치 구간 2]
row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종", m_list, key=f"m{v}")
with row2_col2:
    sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{v}")

# [5:5 배치 구간 3]
row3_col1, row3_col2 = st.columns(2)
with row3_col1: qp = st.number_input("🏭 생산수량", min_value=0, step=1000, key=f"qp{v}")
with row3_col2: qo = st.number_input("📦 발주수량", min_value=0, step=1000, key=f"qo{v}")

# [5:5 배치 구간 4]
row4_col1, row4_col2 = st.columns(2)
with row4_col1: ls = st.number_input("📉 Loss(%)", value=3.0, step=0.5, key=f"ls{v}")
with row4_col2: 
    st.write(" ") # 간격 맞춤
    if st.button("🔄 초기화", use_container_width=True): 
        st.session_state.v += 1; st.rerun()

st.divider()

# 6. 상세 사양 및 결과
f_df = m_df[m_df['강종명'] == sel_m] if sel_m != "전체" else m_df
if sel_t: f_df = f_df[f_df['두께'] == sel_t]
calc = f_df.dropna(subset=['단중']).copy()

if not calc.empty:
    calc['label'] = calc.apply(lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} {x['두께']}T / {x['단중']:.4f}", axis=1)
    sel_s = st.selectbox("🎯 상세 사양 선택", ["선택하세요"] + calc['label'].tolist(), key=f"s{v}")
    
    if st.button("🚀 계산 결과 적용", type="primary", use_container_width=True):
        if sel_s != "선택하세요":
            row = calc[calc['label'] == sel_s].iloc[0]
            uw = float(row['단중'])
            if qp > 0:
                pkg = (uw * qp) * (1 + (ls/100))
                st.success(f"🏭 **생산 필요:** {pkg:,.1f}kg ({pkg/1000:,.2f}ton)")
            if qo > 0:
                okg = (uw * qo) * (1 + (ls/100))
                st.success(f"📦 **발주 필요:** {okg:,.1f}kg ({okg/1000:,.2f}ton)")
else:
    st.warning("데이터 없음")
