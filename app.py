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

# 2. [디자인] 모바일 5:5 배치 및 여백 최적화 CSS
st.markdown("""
<style>
    /* 전체 여백 조절 */
    .main .block-container { padding: 1rem 1rem !important; }
    
    /* 로고 중앙 정렬 및 크기 제한 */
    [data-testid="stImage"] img {
        max-width: 100px !important;
        margin: 0 auto 10px auto;
        display: block;
    }

    /* 입력창 사이의 간격 확보 및 텍스트 겹침 방지 */
    div[data-testid="stSelectbox"], div[data-testid="stTextInput"], div[data-testid="stNumberInput"] {
        margin-bottom: 15px !important;
    }
    
    /* 라벨 스타일 (ㅁㅁ 사이즈용 슬림화) */
    label { 
        font-size: 13px !important; 
        font-weight: bold !important; 
        margin-bottom: -15px !important; /* 라벨과 입력창 사이 낭비 제거 */
    }

    /* [중요] 모바일에서 5:5 강제 가로 배치 */
    @media (max-width: 640px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 8px !important;
        }
        div[data-testid="column"] {
            width: calc(50% - 4px) !important;
            flex: 1 1 calc(50% - 4px) !important;
            min-width: calc(50% - 4px) !important;
        }
    }
    
    .title-text { font-size: 18px !important; font-weight: 800; text-align: center; color: #1E3A8A; margin-bottom: 15px; }
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
            # 칼럼명 매핑 (사용자 환경에 맞게 조정)
            df.rename(columns={'소재명': '강종명', '두께(T)': '두께', '제품 단중': '단중', '기타정보및사양': '프로젝트명'}, inplace=True, errors='ignore')
            if '단중' in df.columns: df['단중'] = pd.to_numeric(df['단중'], errors='coerce')
            return df
        except: return None
    return None

df_raw = load_data()

# 4. [수정] 로그인 화면: 제목 변경 및 여백 확보
if "auth_success" not in st.session_state: st.session_state.auth_success = False
if not st.session_state.auth_success:
    if os.path.exists("logo.png"): st.image("logo.png")
    st.markdown('<p class="title-text">원소재 조회 로그인창</p>', unsafe_allow_html=True)
    
    # 가려지지 않게 순서대로 배치
    user = st.selectbox("👤 사용자 선택", ["선택하세요", "관리자"])
    pw = st.text_input("🔑 비밀번호 입력", type="password")
    
    st.write("") # 추가 여백
    if st.button("로그인", use_container_width=True):
        if pw == "1128": 
            st.session_state.auth_success = True
            st.rerun()
        else:
            st.error("비밀번호를 확인해주세요.")
    st.stop()

# --- 로그인 성공 후 메인 화면 ---

if 'v' not in st.session_state: st.session_state.v = 0
v = st.session_state.v

if os.path.exists("logo.png"): st.image("logo.png")
st.markdown('<p class="title-text">원소재 정보 조회</p>', unsafe_allow_html=True)

# [수정] 고객사 & 프로젝트 5:5 가로 배치
r1_c1, r1_c2 = st.columns(2)
with r1_c1:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사", c_list, key=f"c{v}")
with r1_c2:
    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트", p_list, key=f"p{v}")

# [수정] 강종 & 두께 5:5 가로 배치
r2_c1, r2_c2 = st.columns(2)
with r2_c1:
    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종", m_list, key=f"m{v}")
with r2_c2:
    sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{v}")

# [수정] 생산수량 & 발주수량 5:5 가로 배치
r3_c1, r3_c2 = st.columns(2)
with r3_c1: qp = st.number_input("🏭 생산수량", min_value=0, step=1000, key=f"qp{v}")
with r3_c2: qo = st.number_input("📦 발주수량", min_value=0, step=1000, key=f"qo{v}")

# Loss & 초기화
r4_c1, r4_c2 = st.columns(2)
with r4_c1: ls = st.number_input("📉 Loss(%)", value=3.0, step=0.5, key=f"ls{v}")
with r4_c2:
    st.write("") # 라벨 높이 맞춤용
    st.write("") 
    if st.button("🔄 초기화", use_container_width=True):
        st.session_state.v += 1; st.rerun()

st.divider()

# 결과 조회 영역
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
                pkg = (uw * qp) * (1 + (ls/100))
                st.success(f"🏭 생산 필요량: {pkg:,.1f}kg ({pkg/1000:,.2f}ton)")
            if qo > 0:
                okg = (uw * qo) * (1 + (ls/100))
                st.success(f"📦 발주 필요량: {okg:,.1f}kg ({okg/1000:,.2f}ton)")
else:
    st.warning("조건에 맞는 데이터가 없습니다.")
