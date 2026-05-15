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

# 2. [강력 수정] 로그인창 겹침 방지 및 7cm 화면 5:5 유지 CSS
st.markdown("""
<style>
    /* 전체 화면: 옆으로 절대 안 밀리게 고정 */
    .main .block-container { 
        padding: 1rem 0.5rem !important; 
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    
    /* 로고 크기 축소 */
    [data-testid="stImage"] img { max-width: 80px !important; margin: 0 auto; display: block; }

    /* 로그인 화면 전용: 위젯 간격을 강제로 벌림 */
    div[data-testid="stSelectbox"] { margin-bottom: 40px !important; }
    div[data-testid="stTextInput"] { margin-top: 20px !important; margin-bottom: 30px !important; }

    /* 메인 화면: 7cm 폭에서 한 칸당 3cm(약 48%) 유지 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
    }
    
    div[data-testid="column"] {
        width: 48% !important; /* 위젯 하나당 약 3.3cm */
        flex: 1 1 48% !important;
        min-width: 0 !important;
    }

    /* 슬림 라벨 */
    label { font-size: 12px !important; font-weight: bold !important; margin-bottom: -15px !important; }
    .stSelectbox, .stNumberInput { margin-bottom: -10px !important; }
    .title-text { font-size: 16px !important; font-weight: 800; text-align: center; color: #1E3A8A; margin: 10px 0; }
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
            df.rename(columns={'소재명':'강종명','두께(T)':'두께','제품 단중':'단중','기타정보및사양':'프로젝트명'}, inplace=True, errors='ignore')
            return df
        except: return None
    return None

df_raw = load_data()

# 4. [로그인 화면] 박스 내리기 및 겹침 해결
if "auth_success" not in st.session_state: st.session_state.auth_success = False
if not st.session_state.auth_success:
    if os.path.exists("logo.png"): st.image("logo.png")
    st.markdown('<p class="title-text">원소재 조회 로그인창</p>', unsafe_allow_html=True)
    
    # 1번 박스
    user = st.selectbox("👤 사용자 선택", ["선택하세요", "관리자"])
    
    # 2번 박스 (물리적 간격을 위해 빈 줄 삽입)
    st.write(" ")
    st.write(" ")
    
    pw = st.text_input("🔑 비밀번호 입력", type="password")
    
    st.write(" ")
    if st.button("로그인", use_container_width=True):
        if pw == "1128": st.session_state.auth_success = True; st.rerun()
        else: st.error("정보 불일치")
    st.stop()

# 5. 메인 레이아웃 (7cm 휴대폰 맞춤 ㅁㅁ 배치)
if 'v' not in st.session_state: st.session_state.v = 0
v = st.session_state.v

if os.path.exists("logo.png"): st.image("logo.png")
st.markdown('<p class="title-text">원소재 정보 조회</p>', unsafe_allow_html=True)

# 한 줄에 2개씩 (ㅁㅁ 사이즈)
c1, c2 = st.columns(2)
with c1:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{v}")
with c2:
    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{v}")

c3, c4 = st.columns(2)
with c3:
    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종", m_list, key=f"m{v}")
with c4:
    sel_t = st.number_input
