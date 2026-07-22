import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 설정
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="전우정밀 시스템", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="전우정밀 시스템", page_icon="📊", layout="centered")

# 2. 커스텀 CSS 적용
st.markdown("""
<style>
    /* 전체 배경 및 폰트 설정 */
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    
    .main .block-container { 
        max-width: 650px !important; 
        padding: 2rem 1rem !important; 
    }

    /* 로고 중앙 정렬 */
    [data-testid="stImage"] img { 
        max-width: 130px !important; 
        margin: 0 auto 15px auto; 
        display: block; 
    }

    /* 헤더 카드 스타일 */
    .hero-card {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        padding: 24px 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    
    .hero-title {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #38BDF8 !important;
        margin-bottom: 6px;
    }

    .hero-sub {
        font-size: 13px;
        color: #94A3B8;
        margin: 0;
    }

    /* 라벨 및 위젯 디자인 커스텀 */
    label { 
        font-size: 14px !important; 
        font-weight: 700 !important; 
        color: #E2E8F0 !important;
        margin-bottom: 6px !important; 
    }

    /* 계산 결과 하이라이트 카드 */
    .result-card {
        background: linear-gradient(135deg, #0F172A, #1E293B);
        border: 2px solid #38BDF8;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
    }

    .result-label {
        font-size: 14px;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .result-value {
        font-size: 24px;
        font-weight: 800;
        color: #38BDF8;
    }

    .result-sub {
        font-size: 13px;
        color: #CBD5E1;
        margin-top: 2px;
    }

    /* 구분선 스타일 */
    hr {
        border-color: #334155 !important;
        margin: 25px 0 !important;
    }
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

# 4. 로그인 로직
if "auth_success" not in st.session_state:
    st.session_state.auth_success = False

if not st.session_state.auth_success:
    if os.path.exists("logo.png"): 
        st.image("logo.png")
    
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">원소재 조회 시스템</div>
        <p class="hero-sub">사용자 인증 후 이용하실 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        user = st.selectbox("👤 사용자 선택", ["선택하세요", "관리자"])
        pw = st.text_input("🔑 비밀번호 입력", type="password")
        
        if st.button("로그인", use_container_width=True, type="primary"):
            if pw == "1128":
                st.session_state.auth_success = True
                st.rerun()
            else: 
                st.error("정보가 일치하지 않습니다.")
    st.stop()

# --- 로그인 성공 후 메인 화면 ---

if 'v' not in st.session_state: st.session_state.v = 0
v = st.session_state.v

if os.path.exists("logo.png"): 
    st.image("logo.png")

st.markdown("""
<div class="hero-card">
    <div class="hero-title">📦 원소재 정보 및 소요량 계산기</div>
    <p class="hero-sub">고객사 및 조건별 필요한 원소재 중량을 실시간으로 확인하세요.</p>
</div>
""", unsafe_allow_html=True)

# [조건 선택 입력 영역]
if df_raw is not None:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    sel_c = st.selectbox("🤝 고객사 선택", c_list, key=f"c{v}")

    p_df = df_raw[df_raw['고객사'] == sel_c] if sel_c != '전체' else df_raw
    p_list = ['전체'] + sorted(p_df['프로젝트명'].dropna().unique().tolist())
    sel_p = st.selectbox("📂 프로젝트 선택", p_list, key=f"p{v}")

    m_df = p_df[p_df['프로젝트명'] == sel_p] if sel_p != '전체' else p_df
    m_list = ['전체'] + sorted(m_df['강종명'].dropna().unique().tolist())
    sel_m = st.selectbox("✨ 강종 선택", m_list, key=f"m{v}")

    sel_t = st.number_input("📏 두께(T)", value=None, format="%.2f", key=f"t{v}")

    col1, col2 = st.columns(2)
    with col1:
        qp = st.number_input("🏭 생산수량(EA)", min_value=0, step=1000, key=f"qp{v}")
    with col2:
        qo = st.number_input("📦 발주수량(EA)", min_value=0, step=1000, key=f"qo{v}")

    ls = st.number_input("📉 Loss율(%)", value=3.0, step=0.5, key=f"ls{v}")

    if st.button("🔄 입력 데이터 초기화", use_container_width=True):
        st.session_state.v += 1
        st.rerun()

    st.divider()

    # 결과 조회 영역
    f_df = m_df[m_df['강종명'] == sel_m] if sel_m != "전체" else m_df
    if sel_t: 
        f_df = f_df[f_df['두께'] == sel_t]
    calc = f_df.dropna(subset=['단중']).copy()

    if not calc.empty:
        # 단중 표기를 추가한 드롭다운 라벨 생성
        calc['label'] = calc.apply(
            lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} {x['두께']}T / {x['단중']:.3f}g", 
            axis=1
        )
        
        sel_s = st.selectbox("🎯 상세 사양 선택", ["선택하세요"] + calc['label'].tolist(), key=f"s{v}")
        
        if st.button("🚀 소요량 계산 결과 확인", type="primary", use_container_width=True):
            if sel_s != "선택하세요":
                row = calc[calc['label'] == sel_s].iloc[0]
                uw = float(row['단중'])
                
                if qp > 0:
                    p_kg = (uw * qp) * (1 + (ls/100))
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-label">🏭 생산 필요 원소재 중량</div>
                        <div class="result-value">{p_kg:,.1f} kg</div>
                        <div class="result-sub">({p_kg/1000:,.2f} 톤)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if qo > 0:
                    o_kg = (uw * qo) * (1 + (ls/100))
                    st.markdown(f"""
                    <div class="result-card" style="border-color: #10B981;">
                        <div class="result-label">📦 발주 필요 원소재 중량</div>
                        <div class="result-value" style="color: #10B981;">{o_kg:,.1f} kg</div>
                        <div class="result-sub">({o_kg/1000:,.2f} 톤)</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("조건에 해당하는 원소재 데이터가 존재하지 않습니다.")
else:
    st.error("data.xlsx 파일을 찾을 수 없거나 데이터 로드에 실패했습니다.")
