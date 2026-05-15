import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 설정
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="원소재 정보", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="원소재 정보", page_icon="📊", layout="centered")

# 2. CSS 스타일 최적화
st.markdown("""
<style>
    .main .block-container { padding: 0.5rem 0.8rem; }
    .company-name { font-size: 13px; font-weight: bold; color: #0047AB; margin-bottom: 2px; text-align: center; }
    .app-title { font-size: 18px !important; font-weight: 800; text-align: center; margin-bottom: 15px; }
    
    div[data-testid="stMarkdownContainer"] p { font-size: 14px !important; margin-bottom: -5px; }
    
    div.stButton > button:first-child {
        width: 100%; background-color: #1c83e1; color: white;
        border-radius: 8px; height: 3.5em; font-weight: bold; margin-top: 10px;
    }
    
    .calc-box {
        background-color: rgba(40, 167, 69, 0.15); border: 2px solid #28a745;
        padding: 12px; border-radius: 8px; color: #72ff8d !important;
        font-weight: bold; font-size: 14px; margin-top: 10px; line-height: 1.5;
    }
    .stNumberInput, .stTextInput, .stSelectbox { margin-bottom: -10px; }
</style>
""", unsafe_allow_html=True)

def check_login():
    if "auth_success" not in st.session_state:
        st.session_state.auth_success = False
    if not st.session_state.auth_success:
        col_l, col_m, col_r = st.columns([1, 1, 1])
        with col_m:
            if os.path.exists("logo.png"): st.image("logo.png", width=70)
        st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
        st.markdown('<p class="app-title">원소재 시스템 로그인</p>', unsafe_allow_html=True)
        user_list = ["선택하세요", "관리자"]
        selected_user = st.selectbox("사용자 선택", user_list)
        input_pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if selected_user == "관리자" and input_pw == "1128":
                st.session_state.auth_success = True
                st.rerun()
            else: st.error("정보가 올바르지 않습니다.")
        return False
    return True

if check_login():
    if st.sidebar.button("로그아웃"):
        st.session_state.auth_success = False
        st.rerun()

    @st.cache_data(ttl=600)
    def load_data():
        file_name = "data.xlsx"
        if os.path.exists(file_name):
            try:
                df = pd.read_excel(file_name, engine='openpyxl')
                df.columns = df.columns.str.strip()
                if '제품 단중' in df.columns:
                    df['제품 단중'] = pd.to_numeric(df['제품 단중'], errors='coerce').round(4)
                t_col = next((c for c in df.columns if c in ['두께', '두께(T)', 'T']), None)
                w_col = next((c for c in df.columns if c in ['폭', '폭(W)', 'W', '소재폭']), None)
                if t_col: df[t_col] = pd.to_numeric(df[t_col], errors='coerce').round(1)
                if w_col: df[w_col] = pd.to_numeric(df[w_col], errors='coerce').round(1)
                if '고객사' in df.columns:
                    df['고객사'] = df['고객사'].fillna('미지정')
                return df
            except: return None
        return None

    df = load_data()

    h1, h2 = st.columns([1, 5])
    with h1:
        if os.path.exists("logo.png"): st.image("logo.png", width=40)
    with h2:
        st.markdown('<p class="company-name" style="text-align:left; margin-bottom:0;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
        st.markdown('<p class="app-title" style="text-align:left; font-size:18px !important;">원소재 정보 시스템</p>', unsafe_allow_html=True)

    if df is not None:
        if '고객사' in df.columns:
            customer_list = ['전체'] + sorted(df['고객사'].unique().tolist())
            selected_customer = st.selectbox("🤝 고객사 선택", options=customer_list)
        else: selected_customer = '전체'

        r1c1, r1c2 = st.columns(2)
        with r1c1: name_in = st.text_input("강종명", placeholder="SPFC590").strip()
        with r1c2: thick_in = st.text_input("두께", placeholder="1.3").strip()
        
        r2c1, r2c2 = st.columns(2)
        with r2c1: qty_in = st.number_input("생산 예상수량 (EA)", min_value=0, value=0, step=1000)
        with r2c2: order_qty_in = st.number_input("발주 수량 (EA)", min_value=0, value=0, step=1000)
        
        # Loss율은 가로 전체 너비로 배치 (또는 필요
