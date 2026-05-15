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

# 2. CSS 최적화: 메인 화면 5:5 유지 및 잘림 방지
st.markdown("""
<style>
    /* 전체 여백 조절 */
    .main .block-container { padding: 1rem 0.5rem !important; max-width: 100% !important; overflow-x: hidden !important; }
    
    /* 로고 크기 및 정렬 */
    [data-testid="stImage"] img { max-width: 100px !important; margin: 0 auto; display: block; }
    
    /* 타이틀 스타일 */
    .title-text { font-size: 18px !important; font-weight: 800; text-align: center; color: #1E3A8A; margin: 15px 0; }

    /* [중요] 메인 화면 5:5 가로 배치 (7cm 휴대폰 맞춤) */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
    }
    div[data-testid="column"] {
        width: 48% !important;
        flex: 1 1 48% !important;
        min-width: 0 !important;
    }

    /* 위젯 간격 슬림화 (라벨 겹침 방지를 위해 마진값 양수 고정) */
    label { font-size: 13px !important; font-weight: bold !important; margin-bottom: 5px !important; }
    .stSelectbox, .stNumberInput, .stTextInput { margin-bottom: 15px !important; }
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

# 4. [긴급 수정] 로그인 화면: 겹침 방지를 위한 물리적 배치
if "auth_success" not in st.session_state:
    st.session_state.auth_success = False

if not st.session_state.auth_success:
    if os.path.exists("logo.png"): st.image("logo.png")
    st.markdown('<p class="title-text">원소재 조회 로그인창</p>', unsafe_allow_html=True)
    
    # 컨테이너를 사용하여 위젯 간 독립적인 공간 확보
    with st.container():
        user = st.selectbox("👤 사용자 선택", ["선택하세요", "관리자"])
    
    # 억지로 벌리기 위해 빈 공간 삽입
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    with st.container():
        pw = st.text_input("🔑 비밀번호 입력", type="password")
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
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
    sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{v}")

c5, c6 = st.columns(2)
with c5: qp = st.number_input("🏭 생산수량", min_value=0, step=1000, key=f"qp{v}")
with c6: qo = st.number_input("📦 발주수량", min_value=0, step=1000, key=f"qo{v}")

c7, c8 = st.columns(2)
with c7: ls = st.number_input("📉 Loss(%)", value=3.0, step=0.5, key=f"ls{v}")
with c8:
    st.write(" ") 
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.v += 1; st.rerun()

st.divider()

# 결과 출력
f_df = m_df[m_df['강종명'] == sel_m] if sel_m != "전체" else m_df
if sel_t: f_df = f_df[f_df['두께'] == sel_t]
calc = f_df.dropna(subset=['단중']).copy()

if not calc.empty:
    calc['label'] = calc.apply(lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} {x['두께']}T", axis=1)
    sel_s = st.selectbox("🎯 상세 사양 선택", ["선택하세요"] + calc['label'].tolist(), key=f"s{v}")
    
    if st.button("🚀 계산 적용", type="primary", use_container_width=True):
        if sel_s != "선택하세요":
            row = calc[calc['label'] == sel_s].iloc[0]
            uw = float(row['단중'])
            if qp > 0:
                p_kg = (uw * qp) * (1 + (ls/100))
                st.success(f"🏭 생산: {p_kg:,.1f}kg ({p_kg/1000:,.2f}t)")
            if qo > 0:
                o_kg = (uw * qo) * (1 + (ls/100))
                st.success(f"📦 발주: {o_kg:,.1f}kg ({o_kg/1000:,.2f}t)")
