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

# 2. CSS 스타일 (기존 스타일 유지)
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
</style>
""", unsafe_allow_html=True)

# 3. 로그인 체크 기능 (기존 유지)
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

    # 4. 엑셀 데이터 로드 (기존 data.xlsx 방식)
    @st.cache_data(ttl=600)
    def load_data():
        file_name = "data.xlsx"
        if os.path.exists(file_name):
            try:
                df = pd.read_excel(file_name, engine='openpyxl')
                df.columns = df.columns.str.strip()
                
                # 열 이름 유연하게 찾기
                name_col = next((c for c in df.columns if c in ['소재명', '강종명', '강종']), '소재명')
                thick_col = next((c for c in df.columns if c in ['두께', '두께(T)', 'T']), '두께')
                width_col = next((c for c in df.columns if c in ['폭', '폭(W)', 'W', '소재폭']), '폭')
                weight_col = next((c for c in df.columns if c in ['제품 단중', '단중']), '제품 단중')
                info_col = next((c for c in df.columns if c in ['기타정보및사양', '비고', '사양']), '기타정보및사양')
                
                # 숫자 변환
                if weight_col in df.columns:
                    df[weight_col] = pd.to_numeric(df[weight_col], errors='coerce')
                if thick_col in df.columns:
                    df[thick_col] = pd.to_numeric(df[thick_col], errors='coerce')
                
                return df, name_col, thick_col, width_col, weight_col, info_col
            except: return None, None, None, None, None, None
        return None, None, None, None, None, None

    df, name_col, thick_col, width_col, weight_col, info_col = load_data()

    # 상단 로고 및 제목
    h1, h2 = st.columns([1, 5])
    with h1:
        if os.path.exists("logo.png"): st.image("logo.png", width=40)
    with h2:
        st.markdown('<p class="company-name" style="text-align:left; margin-bottom:0;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
        st.markdown('<p class="app-title" style="text-align:left; font-size:18px !important;">원소재 정보 시스템</p>', unsafe_allow_html=True)

    if df is not None:
        # 고객사 필터링
        customer_list = ['전체'] + sorted(df['고객사'].dropna().unique().tolist()) if '고객사' in df.columns else ['전체']
        selected_customer = st.selectbox("🤝 고객사 선택", options=customer_list)

        res = df.copy()
        if selected_customer != '전체':
            res = res[res['고객사'] == selected_customer]

        # [수정 1] 강종명 드롭박스화
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            available_names = sorted(res[name_col].dropna().unique().tolist()) if name_col in res.columns else []
            name_in = st.selectbox("✨ 강종명 선택", options=["전체"] + available_names)
            if name_in != "전체":
                res = res[res[name_col] == name_in]

        with r1c2:
            # [수정 2] 두께 기본값 공란 처리
            thick_in = st.number_input("📏 두께 (T)", value=None, placeholder="예: 1.3", format="%.2f")
            if thick_in is not None and thick_col in res.columns:
                res = res[res[thick_col] == thick_in]

        # 생산 및 발주 수량
        r2c1, r2c2 = st.columns(2)
        with r2c1: qty_in = st.number_input("생산 예상수량 (EA)", min_value=0, value=0, step=1000)
        with r2c2: order_qty_in = st.number_input("발주 수량 (EA)", min_value=0, value=0, step=1000)
        
        loss_rate = st.number_input("Loss율 (%)", min_value=0.0, max_value=50.0, value=3.0, step=0.5)

        st.divider()

        # [수정 3] 상세 규격 선택 최적화
        if not res.empty:
            calc_ready = res.dropna(subset=[weight_col]).copy() if weight_col in res.columns else pd.DataFrame()
            
            if not calc_ready.empty:
                def make_label(x):
                    # 고객사명 생략 및 사양 정보 강조
                    info = x.get(info_col, '')
                    t = x.get(thick_col, '-')
                    w = x.get(width_col, '-')
                    u = x.get(weight_col, 0)
                    return f"[{info}] {t}t * {w}w / 단중: {u:.4f}kg"

                calc_ready['label'] = calc_ready.apply(make_label, axis=1)
                selected_label = st.selectbox("🎯 상세 규격 선택", options=calc_ready['label'].tolist())
                selected_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]

                if st.button("✅ 설정 내용 적용"):
                    net_unit_w = float(selected_row[weight_col])
                    prod_kg = (net_unit_w * qty_in) * (1 + (loss_rate / 100))
                    order_kg = (net_unit_w * order_qty_in) * (1 + (loss_rate / 100))

                    if qty_in > 0 or order_qty_in > 0:
                        st.markdown(f"""
                        <div class="calc-box">
                            📋 <b>적용 요약</b> (Loss {loss_rate}%)<br>
                            - 사양: {selected_row.get(info_col, '-')}<br>
                            - 규격: {selected_row.get(name_col,'-')} ({selected_row.get(thick_col,'-')} * {selected_row.get(width_col,'-')})<br>
                            - 단중: {net_unit_w:.4f} kg<br><hr style='margin:10px 0; border:0; border-top:1px solid rgba(255,255,255,0.2);'>
                            {"- 🏭 <b>생산 예상 중량</b>: " + f"{prod_kg:,.1f} kg" if qty_in > 0 else ""}
                            {f"<br>- (수량: {qty_in:,} EA)" if qty_in > 0 else ""}
                            {"<br><br>" if qty_in > 0 and order_qty_in > 0 else ""}
                            {"- 📦 <b>고객 발주 중량</b>: " + f"{order_kg:,.1f} kg" if order_qty_in > 0 else ""}
                            {f"<br>- (수량: {order_qty_in:,} EA)" if order_qty_in > 0 else ""}
                        </div>
                        """, unsafe_allow_html=True)
                    else: st.warning("수량을 입력해주세요.")
            else:
                st.info("💡 단중 정보가 입력되지 않은 데이터입니다.")
            
            with st.expander("📊 전체 검색 결과 리스트 보기"):
                st.table(res.astype(str).replace('nan', '-'))
        else:
            st.warning("⚠️ 일치하는 데이터가 엑셀에 없습니다.")
    else:
        st.error("data.xlsx 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
