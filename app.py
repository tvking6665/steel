import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 설정
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="원소재 정보 시스템", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="원소재 정보 시스템", page_icon="📊", layout="centered")

# 2. 모바일 최적화 CSS (여백 축소 및 폰트 조절)
st.markdown("""
<style>
    .main .block-container { padding: 0.5rem 0.5rem; }
    .company-name { font-size: 12px; font-weight: bold; color: #0047AB; text-align: center; margin-bottom: -10px; }
    .app-title { font-size: 16px !important; font-weight: 800; text-align: center; margin-bottom: 5px; }
    div[data-testid="stVerticalBlock"] > div { margin-bottom: -0.5rem; }
    label { font-size: 13px !important; font-weight: 600 !important; margin-bottom: -5px !important; }
    .stNumberInput, .stSelectbox { margin-bottom: -10px !important; }
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

# 4. 로그인 체크
if "auth_success" not in st.session_state: st.session_state.auth_success = False
if not st.session_state.auth_success:
    st.markdown('<p class="app-title">원소재 시스템 로그인</p>', unsafe_allow_html=True)
    user = st.selectbox("사용자", ["선택하세요", "관리자"])
    pw = st.text_input("비밀번호", type="password")
    if st.button("로그인", use_container_width=True):
        if user == "관리자" and pw == "1128":
            st.session_state.auth_success = True
            st.rerun()
    st.stop()

# 5. 상태 및 초기화
if 'v' not in st.session_state: st.session_state.v = 0
def reset():
    st.session_state.v += 1
    st.session_state.apply_clicked = False
    st.rerun()

# 6. 메인 UI (5:5 레이아웃 적용)
ver = st.session_state.v
st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
st.markdown('<p class="app-title">원소재 정보 시스템</p>', unsafe_allow_html=True)

# 고객사 & 프로젝트 (5:5)
c_col, p_col = st.columns(2)
with c_col:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{ver}")
with p_col:
    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{ver}")

# 강종 & 두께 (5:5)
m_col, t_col = st.columns(2)
with m_col:
    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종", m_list, key=f"m{ver}")
with t_col:
    sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{ver}")

# 생산수량 & 발주수량 (5:5)
qp_col, qo_col = st.columns(2)
with qp_col: qp = st.number_input("🏭 생산수량(EA)", min_value=0, step=1000, key=f"qp{ver}")
with qo_col: qo = st.number_input("📦 발주수량(EA)", min_value=0, step=1000, key=f"qo{ver}")

# Loss율 & 초기화 버튼을 한 줄에 (또는 슬림하게)
l_col, b_col = st.columns([2, 1])
with l_col: ls = st.number_input("📉 Loss(%)", value=3.0, step=0.5, key=f"ls{ver}")
with b_col: 
    st.write("") # 간격 맞춤용
    if st.button("🔄 초기화", use_container_width=True): reset()

st.divider()

# 7. 사양 선택 및 결과
f_df = m_df[m_df['강종명'] == sel_m] if sel_m != "전체" else m_df
if sel_t: f_df = f_df[f_df['두께'] == sel_t]
calc = f_df.dropna(subset=['단중']).copy()

if not calc.empty:
    calc['label'] = calc.apply(lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} ({x['두께']}*{x['폭']}) / {x['단중']:.4f}", axis=1)
    sel_s = st.selectbox("🎯 상세 사양 선택", ["선택하세요"] + calc['label'].tolist(), key=f"s{ver}")
    
    if st.button("🚀 계산 결과 적용", type="primary", use_container_width=True):
        st.session_state.apply_clicked = True

    if st.session_state.get('apply_clicked') and sel_s != "선택하세요":
        row = calc[calc['label'] == sel_s].iloc[0]
        uw = float(row['단중'])
        
        # 결과창 (모바일 시인성 강조)
        if qp > 0:
            pkg = (uw * qp) * (1 + (ls/100))
            st.success(f"🏭 **생산 필요량**\n#### :green[`{pkg:,.1f} kg`] ({pkg/1000:,.2f} ton)")
        if qo > 0:
            okg = (uw * qo) * (1 + (ls/100))
            st.success(f"📦 **발주 필요량**\n#### :green[`{okg:,.1f} kg`] ({okg/1000:,.2f} ton)")
        st.info(f"📋 {row['고객사']} | {row['강종명']} | 단중: `{uw:.4f}`")
else:
    st.warning("데이터 없음")
