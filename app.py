import streamlit as st
import pandas as pd
import os
from PIL import Image

# 1. 앱 페이지 설정
try:
    favicon = Image.open("logo.png")
    st.set_page_config(page_title="원소재 정보 시스템", page_icon=favicon, layout="centered")
except:
    st.set_page_config(page_title="원소재 정보 시스템", page_icon="📊", layout="centered")

# 2. CSS 스타일
st.markdown("""
<style>
    .main .block-container { padding: 0.5rem 0.8rem; }
    .company-name { font-size: 13px; font-weight: bold; color: #0047AB; margin-bottom: 2px; text-align: center; }
    .app-title { font-size: 18px !important; font-weight: 800; text-align: center; margin-bottom: 15px; }
    .calc-box {
        background-color: rgba(40, 167, 69, 0.05); border: 1px solid #28a745;
        padding: 15px; border-radius: 10px; color: #ffffff;
        font-size: 15px; margin-top: 10px; line-height: 1.6;
    }
    .highlight { color: #72ff8d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. 로그인 체크
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
    st.stop()

# 4. 데이터 로드 (data.xlsx)
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            df.columns = df.columns.str.strip()
            # 주요 컬럼명 표준화
            df.rename(columns={'소재명': '강종명', '두께(T)': '두께', '폭(W)': '폭', '제품 단중': '단중'}, inplace=True, errors='ignore')
            if '단중' in df.columns:
                df['단중'] = pd.to_numeric(df['단중'], errors='coerce')
            return df
        except: return None
    return None

df_raw = load_data()
if df_raw is None:
    st.error("data.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

# 자동 연동용 콜백 함수
def on_spec_change():
    if "spec_select" in st.session_state and st.session_state.spec_select:
        try:
            target_mat = st.session_state.spec_select.split('] ')[1].split(' (')[0]
            st.session_state.mat_box = target_mat
        except:
            pass

# 헤더 표시
h1, h2 = st.columns([1, 5])
with h1:
    if os.path.exists("logo.png"): st.image("logo.png", width=40)
with h2:
    st.markdown('<p class="company-name" style="text-align:left; margin-bottom:0;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-title" style="text-align:left; font-size:18px !important;">원소재 정보 시스템</p>', unsafe_allow_html=True)

# 5. 입력 필터링
customer_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
selected_customer = st.selectbox("🤝 고객사 선택", options=customer_list)

res = df_raw.copy()
if selected_customer != '전체':
    res = res[res['고객사'] == selected_customer]

r1c1, r1c2 = st.columns(2)
with r1c1:
    available_mats = ["전체"] + sorted(res['강종명'].dropna().unique().tolist())
    name_in = st.selectbox("✨ 강종명 선택", options=available_mats, key="mat_box")

with r1c2:
    thick_in = st.number_input("📏 두께 (T)", value=None, placeholder="", format="%.2f")

r2c1, r2c2 = st.columns(2)
with r2c1: qty_in = st.number_input("생산 예상수량 (EA)", min_value=0, value=0, step=1000)
with r2c2: order_qty_in = st.number_input("발주 수량 (EA)", min_value=0, value=0, step=1000)
loss_rate = st.number_input("Loss율 (%)", value=3.0, step=0.5)

st.divider()

# 6. 상세 사양 선택 (단중 기입 항목만 표시)
filtered_res = res.copy()
if name_in != "전체":
    filtered_res = filtered_res[filtered_res['강종명'] == name_in]
if thick_in is not None:
    filtered_res = filtered_res[filtered_res['두께'] == thick_in]

if '단중' in filtered_res.columns:
    calc_ready = filtered_res.dropna(subset=['단중']).copy()
else:
    calc_ready = pd.DataFrame()

if not calc_ready.empty:
    calc_ready['label'] = calc_ready.apply(
        lambda x: f"[{x.get('기타정보및사양','-')}] {x['강종명']} ({x.get('두께','-')} * {x.get('폭','-')}) / 단중: {x['단중']:.4f}", axis=1
    )
    
    selected_label = st.selectbox(
        "🎯 상세 사양 선택 (단중 기입된 항목만 표시됨)", 
        options=calc_ready['label'].tolist(), 
        key="spec_select",
        on_change=on_spec_change
    )
    
    selected_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]

    if st.button("🚀 계산 결과 적용", type="primary", use_container_width=True):
        unit_w = float(selected_row['단중'])
        # 정확한 중량 계산 공식
        prod_kg = (unit_w * qty_in) * (1 + (loss_rate / 100))
        order_kg = (unit_w * order_qty_in) * (1 + (loss_rate / 100))
        
        # TON 단위 계산
        prod_ton = prod_kg / 1000
        order_ton = order_kg / 1000

        # 결과 요약 HTML (kg/ton 동시 표기 적용)
        summary_html = f"""
        <div class="calc-box">
            <b>📋 적용 요약 (Loss {loss_rate}%)</b><br>
            - 사양: <span class="highlight">{selected_row.get('기타정보및사양','-')}</span><br>
            - 규격: <span class="highlight">{selected_row['강종명']} ({selected_row.get('두께','-')} * {selected_row.get('폭','-')})</span><br>
            - 단중: <span class="highlight">{unit_w:.4f} kg</span>
            <hr style="border:0.5px solid #28a745; opacity:0.3; margin: 10px 0;">
            {'🏭 <b>생산 예상 중량</b>: <span class="highlight">' + f"{prod_kg:,.1f} kg" + '</span> (' + f"{prod_ton:,.2f} ton) / ' + f"{qty_in:,}" + ' EA<br>' if qty_in > 0 else ""}
            {'📦 <b>고객 발주 중량</b>: <span class="highlight">' + f"{order_kg:,.1f} kg" + '</span> (' + f"{order_ton:,.2f} ton) / ' + f"{order_qty_in:,}" + ' EA' if order_qty_in > 0 else ""}
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)
else:
    st.warning("단중 정보가 기입된 데이터가 없습니다.")

if st.sidebar.button("로그아웃"):
    st.session_state.auth_success = False
    st.rerun()
