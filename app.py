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

# 2. CSS 스타일 (제목 및 로고용)
st.markdown("""
<style>
    .main .block-container { padding: 0.5rem 0.8rem; }
    .company-name { font-size: 13px; font-weight: bold; color: #0047AB; margin-bottom: 2px; text-align: center; }
    .app-title { font-size: 18px !important; font-weight: 800; text-align: center; margin-bottom: 15px; }
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

# 4. 데이터 로드
@st.cache_data(ttl=600)
def load_data():
    file_name = "data.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, engine='openpyxl')
            df.columns = df.columns.str.strip()
            df.rename(columns={
                '소재명': '강종명', '두께(T)': '두께', '폭(W)': '폭', 
                '제품 단중': '단중', '기타정보및사양': '프로젝트명'
            }, inplace=True, errors='ignore')
            if '단중' in df.columns:
                df['단중'] = pd.to_numeric(df['단중'], errors='coerce')
            return df
        except: return None
    return None

df_raw = load_data()
if df_raw is None:
    st.error("data.xlsx 파일을 찾을 수 없습니다.")
    st.stop()

# 완전 초기화 함수
def reset_inputs():
    for key in list(st.session_state.keys()):
        if key != "auth_success":
            del st.session_state[key]
    st.rerun()

# 연동용 콜백 함수
def on_spec_change():
    if "spec_select" in st.session_state and st.session_state.spec_select:
        try:
            selected_label = st.session_state.spec_select
            matched_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]
            st.session_state.customer_box = matched_row['고객사']
            st.session_state.project_box = matched_row['프로젝트명']
            st.session_state.mat_box = matched_row['강종명']
            st.session_state.thick_box = float(matched_row['두께'])
        except:
            pass

# 헤더
h1, h2 = st.columns([1, 5])
with h1:
    if os.path.exists("logo.png"): st.image("logo.png", width=40)
with h2:
    st.markdown('<p class="company-name" style="text-align:left; margin-bottom:0;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-title" style="text-align:left; font-size:18px !important;">원소재 정보 시스템</p>', unsafe_allow_html=True)

# 5. 입력 필터링
r0c1, r0c2 = st.columns(2)
with r0c1:
    customer_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    selected_customer = st.selectbox("🤝 고객사 선택", options=customer_list, key="customer_box")

with r0c2:
    project_df = df_raw.copy()
    if selected_customer != '전체':
        project_df = project_df[project_df['고객사'] == selected_customer]
    project_list = ['전체'] + sorted(project_df['프로젝트명'].dropna().unique().tolist()) if '프로젝트명' in project_df.columns else ['전체']
    selected_project = st.selectbox("📂 프로젝트명", options=project_list, key="project_box")

res = df_raw.copy()
if selected_customer != '전체':
    res = res[res['고객사'] == selected_customer]
if selected_project != '전체':
    res = res[res['프로젝트명'] == selected_project]

r1c1, r1c2 = st.columns(2)
with r1c1:
    available_mats = ["전체"] + sorted(res['강종명'].dropna().unique().tolist())
    name_in = st.selectbox("✨ 강종명 선택", options=available_mats, key="mat_box")
with r1c2:
    thick_in = st.number_input("📏 두께 (T)", value=None, placeholder="", format="%.2f", key="thick_box")

r2c1, r2c2 = st.columns(2)
with r2c1: 
    qty_in = st.number_input("생산 예상수량 (EA)", min_value=0, value=0, step=1000, key="prod_qty")
with r2c2: 
    order_qty_in = st.number_input("발주 수량 (EA)", min_value=0, value=0, step=1000, key="order_qty")

loss_rate = st.number_input("Loss율 (%)", value=3.0, step=0.5, key="loss_rate_input")

st.divider()

# 6. 상세 사양 선택
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
        lambda x: f"[{x['프로젝트명']}] {x['강종명']} ({x['두께']} * {x['폭']}) / 단중: {x['단중']:.4f}", axis=1
    )
    
    selected_label = st.selectbox(
        "🎯 상세 사양 선택 (단중 기입 항목만 표시)", 
        options=calc_ready['label'].tolist(), 
        key="spec_select",
        on_change=on_spec_change
    )
    
    selected_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        apply_btn = st.button("🚀 계산 결과 적용", type="primary", use_container_width=True)
    with btn_col2:
        if st.button("🔄 입력 초기화", use_container_width=True):
            reset_inputs()

    if apply_btn:
        unit_w = float(selected_row['단중'])
        
        # 결과 텍스트 구성 (마크다운 활용)
        st.success(f"##### 📋 상세 정보")
        
        info_md = f"""
- **고객사:** {selected_row['고객사']}
- **프로젝트:** {selected_row['프로젝트명']}
- **규격:** {selected_row['강종명']} ({selected_row['두께']} * {selected_row['폭']})
- **단중:** `{unit_w:.4f} kg`
- **※ 적용 요약 (LOSS {loss_rate}%)**
---
"""
        # 생산 예상수량 결과 (값이 있을 때만)
        if qty_in > 0:
            prod_kg = (unit_w * qty_in) * (1 + (loss_rate / 100))
            prod_ton = prod_kg / 1000
            info_md += f"🏭 **생산 예상수량 결과:** \n"
            info_md += f"#### :green[`{prod_kg:,.1f} kg`] ({prod_ton:,.2f} ton) / {qty_in:,} EA  \n\n"

        # 발주 수량 결과 (값이 있을 때만)
        if order_qty_in > 0:
            order_kg = (unit_w * order_qty_in) * (1 + (loss_rate / 100))
            order_ton = order_kg / 1000
            info_md += f"📦 **발주 수량 결과:** \n"
            info_md += f"#### :green[`{order_kg:,.1f} kg`] ({order_ton:,.2f} ton) / {order_qty_in:,} EA"
        
        if qty_in == 0 and order_qty_in == 0:
            info_md += "⚠️ 수량을 입력해주세요."

        st.info(info_md)
else:
    st.warning("선택 조건에 맞는 데이터가 없거나 단중 정보가 비어있습니다.")

if st.sidebar.button("로그아웃"):
    st.session_state.auth_success = False
    st.rerun()
