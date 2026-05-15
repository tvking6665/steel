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

# 2. CSS 스타일
st.markdown("<style>.main .block-container { padding: 0.5rem 0.8rem; } .company-name { font-size: 13px; font-weight: bold; color: #0047AB; text-align: center; } .app-title { font-size: 18px !important; font-weight: 800; text-align: center; }</style>", unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            df.columns = df.columns.str.strip()
            df.rename(columns={'소재명': '강종명', '두께(T)': '두께', '폭(W)': '폭', '제품 단중': '단중', '기타정보및사양': '프로젝트명', '사양': '프로젝트명'}, inplace=True, errors='ignore')
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
    if st.button("로그인"):
        if user == "관리자" and pw == "1128":
            st.session_state.auth_success = True
            st.rerun()
        else: st.error("실패")
    st.stop()

# 5. 초기화 기능
if 'v' not in st.session_state: st.session_state.v = 0
def reset():
    st.session_state.v += 1
    st.session_state.apply_clicked = False
    st.rerun()

# 6. UI 입력 영역
ver = st.session_state.v
st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

r0c1, r0c2 = st.columns(2)
with r0c1:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{ver}")
with r0c2:
    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{ver}")

r1c1, r1c2 = st.columns(2)
with r1c1:
    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종", m_list, key=f"m{ver}")
with r1c2:
    sel_t = st.number_input("📏 두께", value=None, format="%.2f", key=f"t{ver}")

r2c1, r2c2 = st.columns(2)
with r2c1: qp = st.number_input("생산수량(EA)", min_value=0, step=1000, key=f"qp{ver}")
with r2c2: qo = st.number_input("발주수량(EA)", min_value=0, step=1000, key=f"qo{ver}")
ls = st.number_input("Loss율(%)", value=3.0, step=0.5, key=f"ls{ver}")

st.divider()
colb1, colb2 = st.columns(2)
with colb1:
    if st.button("🚀 계산 적용", type="primary", use_container_width=True):
        st.session_state.apply_clicked = True
with colb2:
    if st.button("🔄 초기화", use_container_width=True): reset()

# 7. 사양 선택 및 결과
f_df = m_df[m_df['강종명'] == sel_m] if sel_m != "전체" else m_df
if sel_thick := sel_t: f_df = f_df[f_df['두께'] == sel_thick]
calc = f_df.dropna(subset=['단중']).copy()

if not calc.empty:
    calc['label'] = calc.apply(lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} ({x.get('두께','-')} * {x.get('폭','-')}) / 단중: {x['단중']:.4f}", axis=1)
    opts = ["선택하세요"] + calc['label'].tolist()
    sel_s = st.selectbox("🎯 상세 사양 선택", opts, key=f"s{ver}")

    if st.session_state.get('apply_clicked') and sel_s != "선택하세요":
        row = calc[calc['label'] == sel_s].iloc[0]
        uw = float(row['단중'])
        
        # [수정] 톤(ton) 환산 로직 복구 및 문구 정렬
        if qp > 0:
            pkg = (uw * qp) * (1 + (ls/100))
            st.success(f"🏭 **생산 예상수량 결과:**\n#### 구매필요량 : :green[`{pkg:,.1f} kg`] ({pkg/1000:,.2f} ton) / 생산필요수량 : `{qp:,} EA`")
        if qo > 0:
            okg = (uw * qo) * (1 + (ls/100))
            st.success(f"📦 **발주 수량 결과:**\n#### 구매필요량 : :green[`{okg:,.1f} kg`] ({okg/1000:,.2f} ton) / 발주량 : `{qo:,} EA`")
            
        st.info(f"📋 **상세 정보**\n- 고객사: {row['고객사']} / 프로젝트: {row.get('프로젝트명','-')}\n- 규격: {row['강종명']} ({row['두께']}*{row['폭']}) / 단중: `{uw:.4f} kg` / LOSS: {ls}%")
else: st.warning("데이터 없음")
