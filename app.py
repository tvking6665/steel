import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 설정 (깔끔한 1열 레이아웃을 위해 centered 설정)
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="전우정밀 시스템", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="전우정밀 시스템", page_icon="📊", layout="centered")

# 2. [안정성 최우선] 화면 겹침 방지 CSS
st.markdown("""
<style>
    /* 전체 여백 확보 */
    .main .block-container { padding: 2rem 1rem !important; }
    
    /* 로고 중앙 정렬 */
    [data-testid="stImage"] img { max-width: 120px !important; margin: 0 auto 20px auto; display: block; }
    
    /* 타이틀 스타일 */
    .title-text { font-size: 20px !important; font-weight: 800; text-align: center; color: #1E3A8A; margin-bottom: 25px; }

    /* 위젯 간 간격 넉넉히 확보 (겹침 원천 차단) */
    div[data-testid="stSelectbox"], div[data-testid="stTextInput"], div[data-testid="stNumberInput"] {
        margin-bottom: 20px !important;
    }
    
    /* 라벨 폰트 크기 조절 */
    label { font-size: 15px !important; font-weight: bold !important; margin-bottom: 5px !important; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            df.columns = df.columns.str.strip()
            df.rename(columns={'소재명':'강종명','두께(T)':'두께','폭(W)':'폭','제품 단중':'단중','기타정보및사양':'프로젝트명'}, inplace=True, errors='ignore')
            if '단중' in df.columns: df['단중'] = pd.to_numeric(df['단중'], errors='coerce')
            return df
        except: return None
    return None

df_raw = load_data()

# 4. 로그인 로직 (절대 안 겹치는 표준 수직 배치)
if "auth_success" not in st.session_state:
    st.session_state.auth_success = False

if not st.session_state.auth_success:
    if os.path.exists("logo.png"): st.image("logo.png")
    st.markdown('<p class="title-text">원소재 조회 로그인창</p>', unsafe_allow_html=True)
    
    user = st.selectbox("👤 사용자 선택", ["선택하세요", "관리자"])
    pw = st.text_input("🔑 비밀번호 입력", type="password")
    
    if st.button("로그인", use_container_width=True):
        if pw == "1128":
            st.session_state.auth_success = True
            st.rerun()
        else: st.error("정보가 일치하지 않습니다.")
    st.stop()

# --- 로그인 성공 후 메인 화면 ---

if 'v' not in st.session_state: st.session_state.v = 0
v = st.session_state.v

if os.path.exists("logo.png"): st.image("logo.png")
st.markdown('<p class="title-text">원소재 정보 조회</p>', unsafe_allow_html=True)

# [안정적인 세로(1열) 배치]
c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{v}")

p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{v}")

m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
sel_m = st.selectbox("✨ 강종", m_list, key=f"m{v}")

sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{v}")

qp = st.number_input("🏭 생산수량(EA)", min_value=0, step=1000, key=f"qp{v}")
qo = st.number_input("📦 발주수량(EA)", min_value=0, step=1000, key=f"qo{v}")
ls = st.number_input("📉 Loss율(%)", value=3.0, step=0.5, key=f"ls{v}")

if st.button("🔄 입력 데이터 초기화", use_container_width=True):
    st.session_state.v += 1; st.rerun()

st.divider()

# 결과 조회 영역
f_df = m_df[m_df['강종명'] == sel_m] if sel_m != "전체" else m_df
if sel_t: f_df = f_df[f_df['두께'] == sel_t]
calc = f_df.dropna(subset=['단중']).copy()

if not calc.empty:
    calc['label'] = calc.apply(lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} {x['두께']}T", axis=1)
    sel_s = st.selectbox("🎯 상세 사양 선택", ["선택하세요"] + calc['label'].tolist(), key=f"s{v}")
    
    if st.button("🚀 계산 결과 적용", type="primary", use_container_width=True):
        if sel_s != "선택하세요":
            row = calc[calc['label'] == sel_s].iloc[0]
            uw = float(row['단중'])
            if qp > 0:
                p_kg = (uw * qp) * (1 + (ls/100))
                st.success(f"🏭 생산 필요량: **{p_kg:,.1f}kg** ({p_kg/1000:,.2f}t)")
            if qo > 0:
                o_kg = (uw * qo) * (1 + (ls/100))
                st.success(f"📦 발주 필요량: **{o_kg:,.1f}kg** ({o_kg/1000:,.2f}t)")
else:
    st.warning("데이터가 없습니다.")
