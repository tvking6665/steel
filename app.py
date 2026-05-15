import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 설정
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

# 2. CSS 스타일 최적화 (모바일 글자 크기 조정 및 로그인 박스 개선)
st.markdown("""
<style>
    /* 전체 모바일 여백 조정 */
    .main .block-container { padding: 1rem 1rem; }
    
    /* 회사명 및 제목 크기 최적화 */
    .company-name { font-size: 14px; font-weight: bold; color: #0047AB; margin-bottom: 5px; text-align: center; }
    .app-title { font-size: 20px !important; font-weight: 800; text-align: center; margin-bottom: 20px; }
    
    /* 로그인 라벨 글자 크기 */
    div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; }
    
    /* 버튼 스타일 */
    div.stButton > button:first-child {
        width: 100%;
        background-color: #1c83e1;
        color: white;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        margin-top: 15px;
    }
    
    /* 조회 결과 및 요약 박스 */
    .search-result-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1.5px solid #1c83e1;
        padding: 10px;
        border-radius: 8px;
        color: #58a6ff !important;
        font-weight: bold;
        font-size: 14px;
        margin: 10px 0px;
    }
    
    .calc-box {
        background-color: rgba(40, 167, 69, 0.15);
        border: 2px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        color: #72ff8d !important;
        font-weight: bold;
        font-size: 15px;
        margin-top: 15px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# [수정] 로그인 관리 로직 (로고 배치 및 글자 크기 반영)
# ---------------------------------------------------------
def check_login():
    if "auth_success" not in st.session_state:
        st.session_state.auth_success = False

    if not st.session_state.auth_success:
        # 로고 중앙 배치
        col_l, col_m, col_r = st.columns([1, 1, 1])
        with col_m:
            if os.path.exists("logo.png"):
                st.image("logo.png", width=80)
        
        st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
        st.markdown('<p class="app-title">원소재 정보 시스템 로그인</p>', unsafe_allow_html=True)
        
        # 로그인 입력창 (너비 조정)
        user_list = ["선택하세요", "관리자"]
        selected_user = st.selectbox("사용자 선택", user_list)
        input_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        
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

# 로그인 통과 시 메인 화면 실행
if check_login():
    # 사이드바 로그아웃
    st.sidebar.markdown(f"**{st.session_state.get('user_name', '관리자')}**님 접속 중")
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

    # 메인 상단 헤더
    h_col1, h_col2 = st.columns([1, 4])
    with h_col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=50)
    with h_col2:
        st.markdown('<p class="company-name" style="text-align:left;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
        st.markdown('<a href="http://mes.jwjm.com/bang.asp" target="_blank" style="text-decoration:none; font-size:11px; color:#E60012; font-weight:bold;">📊 실시간 가동 현황판</a>', unsafe_allow_html=True)

    st.markdown('<p class="app-title" style="text-align:left; font-size:22px !important;">원소재 정보 시스템</p>', unsafe_allow_html=True)

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
                    cust = get_val(x, ['고객사'])
                    return f"[{cust}] {x['소재명']} (T:{t} / W:{w} / 단중:{x['제품 단중']})"

                calc_ready['label'] = calc_ready.apply(make_label, axis=1)
                selected_label = st.selectbox("🎯 상세 규격 선택", options=calc_ready['label'].tolist())
                selected_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]
                
                if st.button("✅ 설정 내용 적용"):
                    if qty_in > 0:
                        net_unit_w = float(selected_row['제품 단중'])
                        total_net_kg = net_unit_w * qty_in
                        total_gross_kg = total_net_kg * (1 + (loss_rate / 100))
                        total_gross_ton = total_gross_kg / 1000
                        
                        st.markdown(f"""
                        <div class="calc-box">
                            📋 최종 적용 요약 (Loss {loss_rate}% 반영)<br>
                            - 고객사: {get_val(selected_row, ['고객사'])}<br>
                            - 규격: {selected_row['소재명']}<br>
                            - 제품 단중: {net_unit_w} kg<br>
                            - 예상 수량: {qty_in:,} EA<br><br>
                            - 📦 순수 소요량: {total_net_kg:,.0f} kg<br>
                            - 🚚 **총 구매 예정량: {total_gross_kg:,.0f} kg ({total_gross_ton:,.1f} ton)**
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("수량을 입력해주세요.")
            else:
                st.info("💡 단중 정보가 없습니다.")

            with st.expander("📊 상세 시트 보기"):
                st.table(res.astype(str).replace('nan', '-'))
        else:
            st.warning("데이터가 없습니다.")
    else:
        st.error("data.xlsx 파일을 확인해주세요.")
