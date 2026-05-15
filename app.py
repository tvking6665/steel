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

# 2. 모바일 시인성 개선 커스텀 CSS
st.markdown("""
<style>
    /* 전체 여백 최적화 */
    .main .block-container { padding: 1rem 0.8rem !important; }
    
    /* 로고 사이즈 및 정렬 */
    [data-testid="stImage"] img {
        max-width: 100px !important;
        margin: 0 auto;
        display: block;
    }

    /* 로그인창 문구 및 타이틀 스타일 */
    .login-title { font-size: 18px; font-weight: 800; text-align: center; color: #1E3A8A; margin: 15px 0; }
    
    /* 입력 위젯 간격 확보 (겹침 방지) */
    div[data-testid="stSelectbox"], div[data-testid="stTextInput"], div[data-testid="stNumberInput"] {
        margin-bottom: 20px !important;
    }
    
    /* 라벨 크기 최적화 */
    label { font-size: 14px !important; font-weight: bold !important; margin-bottom: 5px !important; }

    /* 모바일에서 억지 가로 배치 대신 안정적인 2열 구성 */
    [data-testid="column"] {
        width: 48% !important;
        flex: 1 1 48% !important;
        min-width: 48% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }
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

# 4. 로그인 화면 (제목 수정 및 겹침 해결)
if "auth_success" not in st.session_state: st.session_state.auth_success = False
if not st.session_state.auth_success:
    if os.path.exists("logo.png"): st.image("logo.png")
    st.markdown('<p class="login-title">원소재 조회 로그인창</p>', unsafe_allow_html=True)
    
    # 겹치지 않도록 간격을 둔 수직 배치
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
st.markdown('<p class="login-title">원소재 정보 조회</p>', unsafe_allow_html=True)

# 🤝 고객사 & 📂 프로젝트 (5:5 가로 배치)
r1c1, r1c2 = st.columns(2)
with r1c1:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{v}")
with r1c2:
    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{v}")

# ✨ 강종 & 📏 두께 (5:5 가로 배치)
r2c1, r2c2 = st.columns(2)
with r2c1:
    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종", m_list, key=f"m{v}")
with r2c2:
    sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{v}")

# 🏭 생산수량 & 📦 발주수량 (5:5 가로 배치)
r3c1, r3c2 = st.columns(2)
with r3c1: qp = st.number_input("🏭 생산수량", min_value=0, step=1000, key=f"qp{v}")
with r3c2: qo = st.number_input("📦 발주수량", min_value=0, step=1000, key=f"qo{v}")

# 📉 Loss & 🔄 초기화 (5:5 가로 배치)
r4c1, r4c2 = st.columns(2)
with r4c1: ls = st.number_input("📉 Loss(%)", value=3.0, step=0.5, key=f"ls{v}")
with r4c2:
    st.write("") # 라벨 높이 맞춤용
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.v += 1; st.rerun()

st.divider()

# 결과 조회
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
                pkg = (uw * qp) * (1 + (ls/100))
                st.success(f"🏭 생산 필요량: {pkg:,.1f}kg ({pkg/1000:,.2f}ton)")
            if qo > 0:
                okg = (uw * qo) * (1 + (ls/100))
                st.success(f"📦 발주 필요량: {okg:,.1f}kg ({okg/1000:,.2f}ton)")
