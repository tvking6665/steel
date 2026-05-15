import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 설정 (휴대폰 아이콘 및 로고 설정)
try:
    favicon = Image.open("logo.png")
    st.set_page_config(
        page_title="원소재 정보", 
        page_icon=favicon,       
        layout="centered"
    )
except:
    st.set_page_config(
        page_title="원소재 정보",
        page_icon="📊",
        layout="centered"
    )

# 2. CSS 스타일 최적화 (로그인 박스 스타일 추가)
st.markdown("""
<style>
    .main .block-container { padding: 1rem 0.5rem; }
    .company-name { font-size: 14px; font-weight: bold; color: #0047AB; margin-bottom: 2px; }
    .app-title { font-size: 22px; font-weight: 800; margin-top: 0px; margin-bottom: 10px; }
    
    /* 버튼 스타일 */
    div.stButton > button:first-child {
        width: 100%;
        background-color: #1c83e1;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        margin-top: 10px;
    }
    
    /* 조회 결과 박스 */
    .search-result-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1.5px solid #1c83e1;
        padding: 10px;
        border-radius: 8px;
        color: #58a6ff !important;
        font-weight: bold;
        margin: 10px 0px;
    }
    
    /* 최종 요약 박스 */
    .calc-box {
        background-color: rgba(40, 167, 69, 0.15);
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        color: #72ff8d !important;
        font-weight: bold;
        font-size: 16px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# [추가] 로그인 관리 로직
# ---------------------------------------------------------
def check_login():
    if "auth_success" not in st.session_state:
        st.session_state.auth_success = False

    if not st.session_state.auth_success:
        st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="app-title">🔐 원소재 시스템 로그인</h1>', unsafe_allow_html=True)
        
        with st.container():
            user_list = ["선택하세요", "관리자"]
            selected_user = st.selectbox("사용자 선택", user_list)
            input_pw = st.text_input("비밀번호", type="password")
            
            if st.button("로그인"):
                if selected_user == "관리자" and input_pw == "1128":
                    st.session_state.auth_success = True
                    st.rerun()
                elif selected_user == "선택하세요":
                    st.warning("사용자를 선택해주세요.")
                else:
                    st.error("비밀번호가 틀렸습니다.")
        return False
    return True

# 로그인 통과 시에만 아래 코드 실행
if check_login():
    # 로그아웃 버튼 (사이드바)
    if st.sidebar.button("로그아웃"):
        st.session_state.auth_success = False
        st.rerun()

    # 3. 데이터 로드 및 전처리
    @st.cache_data(ttl=600)
    def load_data():
        file_name = "data.xlsx"
        if os.path.exists(file_name):
            try:
                df = pd.read_excel(file_name, engine='openpyxl')
                df.columns = df.columns.str.strip()
                if '고객사' in df.columns:
                    df['고객사'] = df['고객사'].fillna('미지정')
                return df
            except:
                return None
        return None

    def get_val(row, cols):
        for c in cols:
            if c in row.index and pd.notnull(row[c]):
                return row[c]
        return "-"

    df = load_data()

    # 4. 상단 헤더 영역
    h_col1, h_col2 = st.columns([1, 4])
    with h_col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=60)
    with h_col2:
        st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
        st.markdown('<a href="http://mes.jwjm.com/bang.asp" target="_blank" style="text-decoration:none; font-size:12px; color:#E60012; font-weight:bold;">📊 실시간 가동 현황판</a>', unsafe_allow_html=True)

    st.markdown('<h1 class="app-title">원소재 정보 시스템</h1>', unsafe_allow_html=True)

    if df is not None:
        # 5. 입력 및 필터 영역
        st.write("🔍 **소재 검색 및 조건 입력**")
        
        if '고객사' in df.columns:
            customer_list = ['전체'] + sorted(df['고객사'].unique().tolist())
            selected_customer = st.selectbox("🤝 고객사 선택", options=customer_list)
        else:
            selected_customer = '전체'

        c1, c2 = st.columns(2)
        with c1:
            name_in = st.text_input("강종명", placeholder="예: SPFC590").strip()
        with c2:
            thick_in = st.text_input("두께", placeholder="예: 1.3").strip()
        
        c3, c4 = st.columns(2)
        with c3:
            qty_in = st.number_input("생산 예상 수량 (EA)", min_value=0, value=0, step=1000)
        with c4:
            loss_rate = st.number_input("Loss율 (%)", min_value=0.0, max_value=50.0, value=3.0, step=0.5)

        # 필터링 로직
        res = df.copy()
        if selected_customer != '전체':
            res = res[res['고객사'] == selected_customer]
        if name_in:
            res = res[res['소재명'].astype(str).str.contains(name_in, case=False, na=False)]
        if thick_in:
            t_col = '두께(T)' if '두께(T)' in res.columns else '두께'
            try:
                res = res[res[t_col].astype(float) == float(thick_in)]
            except:
                pass

        st.divider()

        # 6. 조회 결과 및 계산 영역
        if not res.empty:
            calc_ready = res.dropna(subset=['제품 단중']).copy()
            st.markdown(f'<div class="search-result-box">✅ 조회 결과: {len(res)}건</div>', unsafe_allow_html=True)
            
            if not calc_ready.empty:
                def make_label(x):
                    t = get_val(x, ['두께','두께(T)','T'])
                    w = get_val(x, ['폭','폭(W)','W','소재폭'])
                    extra = get_val(x, ['기타 정보 및 사양', '기타정보', '비고'])
                    cust = get_val(x, ['고객사'])
                    return f"[{cust}] {x['소재명']} (두께:{t} / 폭:{w} / 단중:{x['제품 단중']}) - {extra}"

                calc_ready['label'] = calc_ready.apply(make_label, axis=1)
                selected_label = st.selectbox("🎯 정확한 상세 규격 선택", options=calc_ready['label'].tolist())
