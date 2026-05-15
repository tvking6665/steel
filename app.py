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
</style>
""", unsafe_allow_html=True)

# 3. 로그인 체크 및 초기 세션 설정
if "auth_success" not in st.session_state:
    st.session_state.auth_success = False

# [수정] 초기 상태를 '전체/공란'으로 설정하는 함수
def init_session_state():
    st.session_state.customer_box = "전체"
    st.session_state.project_box = "전체"
    st.session_state.mat_box = "전체"
    st.session_state.thick_box = None
    st.session_state.prod_qty = 0
    st.session_state.order_qty = 0
    if "spec_select" in st.session_state:
        del st.session_state.spec_select

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
            init_session_state() # 로그인 성공 시 초기화 호출
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
    init_session_state()
    st.rerun()

# 연동용 콜백 함수 (수동 선택 시에만 작동하도록 보강)
def on_spec_change():
    if "spec_select" in st.session_state and st.session_state.spec_select:
        try:
            selected_label = st.session_state.spec_select
            matched_row = df_raw.copy()
            matched_row['label_temp'] = matched_row.apply(
                lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} ({x.get('두께','-')} * {x.get('폭','-')}) / 단중: {x['단중']:.4f}", axis=1
            )
            target = matched_row[matched_row['label_temp'] == selected_label].iloc[0]
            st.session_state.customer_box = target['고객사']
            st.session_state.project_box = target.get('프로젝트명','전체')
            st.session_state.mat_box = target['강종명']
            st.session_state.thick_box = float(target['두께'])
        except: pass

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
    st.selectbox("🤝 고객사 선택", options=customer_list, key="customer_box")

with r0c2:
    project_df = df_raw.copy()
    if st.session_state.customer_box != '전체':
        project_df = project_df[project_df['고객사'] == st.session_state.customer_box]
    project_list = ['전체'] + sorted(project_df['프로젝트명'].dropna().unique().tolist()) if '프로젝트명' in project_df.columns else ['전체']
    st.selectbox("📂 프로젝트명", options=project_list, key="project_box")

r1c1, r1c2 = st.columns(2)
with r1c1:
    res = df_raw.copy()
    if st.session_state.customer_box != '전체':
        res = res[res['고객사'] == st.session_state.customer_box]
    if st.session_state.project_box != '전체':
        res = res[res['프로젝트명'] == st.session_state.project_box]
    available_mats = ["전체"] + sorted(res['강종명'].dropna().unique().tolist())
    st.selectbox("✨ 강종명 선택", options=available_mats, key="mat_box")
with r1c2:
    st.number_input("📏 두께 (T)", value=None, placeholder="", format="%.2f", key="thick_box")

r2c1, r2c2 = st.columns(2)
with r2c1: 
    st.number_input("생산 예상수량 (EA)", min_value=0, step=1000, key="prod_qty")
with r2c2: 
    st.number_input("발주 수량 (EA)", min_value=0, step=1000, key="order_qty")

loss_rate = st.number_input("Loss율 (%)", value=3.0, step=0.5, key="loss_rate_input")

st.divider()

# 6. 상세 사양 선택
filtered_res = res.copy()
if st.session_state.mat_box != "전체":
    filtered_res = filtered_res[filtered_res['강종명'] == st.session_state.mat_box]
if st.session_state.thick_box is not None:
    filtered_res = filtered_res[filtered_res['두께'] == st.session_state.thick_box]

calc_ready = filtered_res.dropna(subset=['단중']).copy() if '단중' in filtered_res.columns else pd.DataFrame()

if not calc_ready.empty:
    calc_ready['label'] = calc_ready.apply(
        lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} ({x.get('두께','-')} * {x.get('폭','-')}) / 단중: {x['단중']:.4f}", axis=1
    )
    
    # [수정] 첫 줄 자동 선택 방지를 위해 빈 값 추가
    spec_options = ["선택하세요"] + calc_ready['label'].tolist()
    selected_label = st.selectbox(
        "🎯 상세 사양 선택 (단중 기입 항목만 표시)", 
        options=spec_options, 
        key="spec_select",
        on_change=on_spec_change
    )
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        apply_btn = st.button("🚀 계산 결과 적용", type="primary", use_container_width=True)
    with btn_col2:
        if st.button("🔄 입력 초기화", use_container_width=True):
            reset_inputs()

    if apply_btn and selected_label != "선택하세요":
        target_row = calc_ready[calc_ready['label'] == selected_label].iloc[0]
        unit_w = float(target_row['단중'])
        
        # 상단 형광색 결과 표시
        result_md = ""
        if st.session_state.prod_qty > 0:
            prod_kg = (unit_w * st.session_state.prod_qty) * (1 + (loss_rate / 100))
            result_md += f"🏭 **생산 예상수량 결과:** \n #### :green[`{prod_kg:,.1f} kg`] ({prod_kg/1000:,.2f} ton) / {st.session_state.prod_qty:,} EA  \n\n"
        if st.session_state.order_qty > 0:
            order_kg = (unit_w * st.session_state.order_qty) * (1 + (loss_rate / 100))
            result_md += f"📦 **발주 수량 결과:** \n #### :green[`{order_kg:,.1f} kg`] ({order_kg/1000:,.2f} ton) / {st.session_state.order_qty:,} EA"
        
        if st.session_state.prod_qty == 0 and st.session_state.order_qty == 0:
            result_md = "⚠️ 수량을 입력해주세요."
        st.success(result_md)

        # 하단 상세 정보
        info_md = f"""
### 📋 상세 정보
- **고객사:** {target_row['고객사']}
- **프로젝트:** {target_row.get('프로젝트명','-')}
- **규격:** {target_row['강종명']} ({target_row.get('두께','-')} * {target_row.get('폭','-')})
- **단중:** `{unit_w:.4f} kg`
- **※ 적용 요약 (LOSS {loss_rate}%)**
"""
        st.info(info_md)
    elif apply_btn and selected_label == "선택하세요":
        st.warning("상세 사양을 먼저 선택해주세요.")
else:
    st.warning("조건에 맞는 데이터가 없습니다. [입력 초기화] 후 다시 시도해 주세요.")

if st.sidebar.button("🚪 로그아웃"):
    st.session_state.auth_success = False
    st.rerun()
