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

# 2. [강력 수정] 5:5 배치를 위한 커스텀 스타일
st.markdown("""
<style>
    /* 전체 여백 및 배경 */
    .main .block-container { padding: 0.5rem 0.5rem !important; }
    
    /* 로고 중앙 정렬 및 크기 대폭 축소 */
    [data-testid="stImage"] img {
        max-width: 100px !important;
        margin: 0 auto;
        display: block;
    }

    /* 한 줄에 2개씩 강제 배치 (5:5) */
    [data-testid="column"] {
        flex: 1 1 48% !important;
        min-width: 48% !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 5px !important;
        display: flex !important;
        flex-direction: row !important;
    }

    /* 위젯 크기 및 라벨 슬림화 */
    label { font-size: 13px !important; font-weight: bold !important; margin-bottom: -15px !important; }
    .stSelectbox, .stNumberInput { margin-bottom: -12px !important; }
    
    /* 타이틀 및 텍스트 스타일 */
    .title-text { font-size: 16px !important; font-weight: 800; text-align: center; color: #1E3A8A; margin-top: 5px; }
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

# 4. 로그인 체크 (로고 사이즈 조정 반영)
if "auth_success" not in st.session_state: st.session_state.auth_success = False
if not st.session_state.auth_success:
    if os.path.exists("logo.png"): st.image("logo.png")
    st.markdown('<p class="title-text">LOGIN</p>', unsafe_allow_html=True)
    user = st.selectbox("사용자", ["선택하세요", "관리자"])
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인", use_container_width=True):
        if pw == "1128": st.session_state.auth_success = True; st.rerun()
    st.stop()

# 5. 메인 UI (5:5 배치)
if 'v' not in st.session_state: st.session_state.v = 0
v = st.session_state.v

if os.path.exists("logo.png"): st.image("logo.png")
st.markdown('<p class="title-text">RAW MATERIAL SYSTEM</p>', unsafe_allow_html=True)

# 고객사-프로젝트 (5:5)
r1_c1, r1_c2 = st.columns(2)
with r1_c1:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{v}")
with r1_c2:
    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{v}")

# 강종-두께 (5:5)
r2_c1, r2_c2 = st.columns(2)
with r2_c1:
    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종", m_list, key=f"m{v}")
with r2_c2:
    sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{v}")

# 수량 (5:5)
r3_c1, r3_c2 = st.columns(2)
with r3_c1: qp = st.number_input("🏭 생산수량", min_value=0, step=1000, key=f"qp{v}")
with r3_c2: qo = st.number_input("📦 발주수량", min_value=0, step=1000, key=f"qo{v}")

# Loss-초기화 (5:5)
r4_c1, r4_c2 = st.columns(2)
with r4_c1: ls = st.number_input("📉 Loss(%)", value=3.0, step=0.5, key=f"ls{v}")
with r4_c2:
    st.write(" ") # 높이 맞춤
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.v += 1; st.rerun()

st.divider()

# 6. 상세 사양 및 결과
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
                st.success(f"🏭 **생산 필요:** {pkg:,.1f}kg ({pkg/1000:,.2f}ton)")
            if qo > 0:
                okg = (uw * qo) * (1 + (ls/100))
                st.success(f"📦 **발주 필요:** {okg:,.1f}kg ({okg/1000:,.2f}ton)")
else:
    st.warning("데이터 없음")
