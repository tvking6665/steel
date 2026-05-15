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

# 2. CSS
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

# 4. 로그인
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

# 5. 상태 관리
if 'v' not in st.session_state: st.session_state.v = 0
if 'c' not in st.session_state: st.session_state.c = "전체"
if 'p' not in st.session_state: st.session_state.p = "전체"
if 'm' not in st.session_state: st.session_state.m = "전체"
if 't' not in st.session_state: st.session_state.t = None

def reset():
    st.session_state.v += 1
    st.session_state.c, st.session_state.p, st.session_state.m, st.session_state.t = "전체", "전체", "전체", None
    if 'last' in st.session_state: del st.session_state.last
    st.rerun()

# 6. UI 입력
ver = st.session_state.v
st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)

r0c1, r0c2 = st.columns(2)
c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
with r0c1: 
    sel_c = st.selectbox("🤝 고객사", c_list, index=c_list.index(st.session_state.c) if st.session_state.c in c_list else 0, key=f"c{ver}")
    st.session_state.c = sel_c

p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
with r0c2: 
    sel_p = st.selectbox("📂 프로젝트", p_list, index=p_list.index(st.session_state.p) if st.session_state.p in p_list else 0, key=f"p{ver}")
    st.session_state.p = sel_p

r1c1, r1c2 = st.columns(2)
m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
with r1c1: 
    sel_m = st.selectbox("✨ 강종", m_list, index=m_list.index(st.session_state.m) if st.session_state.m in m_list else 0, key=f"m{ver}")
    st.session_state.m = sel_m
with r1c2: 
    sel_t = st.number_input("📏 두께", value=st.session_state.t, format="%.2f", key=f"t{ver}")
    st.session_state.t = sel_t

r2c1, r2c2 = st.columns(2)
with r2c1: qp = st.number_input("생산수량", min_value=0, step=1000, key=f"qp{ver}")
with r2c2: qo = st.number_input("발주수량", min_value=0, step=1000, key=f"qo{ver}")
ls = st.number_input("Loss(%)", value=3.0, step=0.5, key=f"ls{ver}")

st.divider()
colb1, colb2 = st.columns(2)
with colb1: apply = st.button("🚀 계산 적용", type="primary", use_container_width=True)
with colb2: 
    if st.button("🔄 초기화", use_container_width=True): reset()

# 7. 사양 선택 및 강제 연동
f_df = m_df[m_df['강종명'] == sel_m] if sel_m != "전체" else m_df
if sel_t: f_df = f_df[f_df['두께'] == sel_t]
calc = f_df.dropna(subset=['단중']).copy()

if not calc.empty:
    calc['label'] = calc.apply(lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} ({x.get('두께','-')} * {x.get('폭','-')}) / 단중: {x['단중']:.4f}", axis=1)
    opts = ["선택하세요"] + calc['label'].tolist()
    sel_s = st.selectbox("🎯 상세 사양 선택", opts, key=f"s{ver}")

    # [중요] 선택 즉시 세션 강제 주입 및 리런
    if sel_s != "선택하세요" and sel_s != st.session_state.get('last'):
        row = calc[calc['label'] == sel_s].iloc[0]
        st.session_state.c, st.session_state.p, st.session_state.m, st.session_state.t = row['고객사'], row.get('프로젝트명','전체'), row['강종명'], float(row['두께'])
        st.session_state.last = sel_s
        st.rerun()

    if apply and sel_s != "선택하세요":
        row = calc[calc['label'] == sel_s].iloc[0]
        uw = float(row['단중'])
        if qp > 0:
            pkg = (uw * qp) * (1 + (ls/100))
            st.success(f"🏭 **생산 결과:**\n#### 구매필요: :green[`{pkg:,.1f} kg`] / 생산수량: `{qp:,} EA`")
        if qo > 0:
            okg = (uw * qo) * (1 + (ls/100))
            st.success(f"📦 **발주 결과:**\n#### 구매필요: :green[`{okg:,.1f} kg`] / 발주량: `{qo:,} EA`")
        st.info(f"📋 **상세:** {row['고객사']} / {row['강종명']} ({row['두께']}*{row['폭']}) / 단중: `{uw:.4f}`")
else: st.warning("데이터 없음")
