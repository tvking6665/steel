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

# 3. 데이터 로드
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

# 4. 로그인 체크
if "auth_success" not in st.session_state:
    st.session_state.auth_success = False

if not st.session_state.auth_success:
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        if os.path.exists("logo.png"): st.image("logo.png", width=70)
    st.markdown('<p class="company-name">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-title">원소재 시스템 로그인</p>', unsafe_allow_html=True)
    selected_user = st.selectbox("사용자 선택", ["선택하세요", "관리자"])
    input_pw = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if selected_user == "관리자" and input_pw == "1128":
            st.session_state.auth_success = True
            st.rerun()
        else: st.error("정보가 올바르지 않습니다.")
    st.stop()

# 5. [중요] 초기화 및 상태 관리
# 에러를 방지하기 위해 위젯 번호를 바꿔 전체를 리셋시키는 방식 사용
if 'form_version' not in st.session_state:
    st.session_state.form_version = 0

def reset_all():
    # 위젯 버전 번호를 올려서 모든 위젯을 강제로 초기화시킴 (가장 안전한 에러 방지책)
    st.session_state.form_version += 1
    st.session_state.apply_clicked = False
    st.rerun()

# 연동용 콜백 함수
def on_spec_change():
    if f"spec_select_{st.session_state.form_version}" in st.session_state:
        label = st.session_state[f"spec_select_{st.session_state.form_version}"]
        if label != "선택하세요":
            try:
                matched_row = df_raw.copy()
                matched_row['label_temp'] = matched_row.apply(
                    lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} ({x.get('두께','-')} * {x.get('폭','-')}) / 단중: {x['단중']:.4f}", axis=1
                )
                target = matched_row[matched_row['label_temp'] == label].iloc[0]
                # 세션에 값 저장 (위젯 key와 분리하여 저장)
                st.session_state.cur_customer = target['고객사']
                st.session_state.cur_project = target.get('프로젝트명','전체')
                st.session_state.cur_mat = target['강종명']
                st.session_state.cur_thick = float(target['두께'])
            except: pass

# 메인 UI 헤더
h1, h2 = st.columns([1, 5])
with h1:
    if os.path.exists("logo.png"): st.image("logo.png", width=40)
with h2:
    st.markdown('<p class="company-name" style="text-align:left; margin-bottom:0;">Jeon Woo Precision Co., LTD</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-title" style="text-align:left; font-size:18px !important;">원소재 정보 시스템</p>', unsafe_allow_html=True)

# 6. 입력 영역 (form_version을 key에 포함시켜 에러 방지)
v = st.session_state.form_version

r0c1, r0c2 = st.columns(2)
with r0c1:
    c_list = ['전체'] + sorted(df_raw['고객사'].dropna().unique().tolist())
    # 연동된 값이 있으면 index를 찾고, 없으면 0(전체)
    c_idx = c_list.index(st.session_state.get('cur_customer', '전체')) if st.session_state.get('cur_customer') in c_list else 0
    selected_customer = st.selectbox("🤝 고객사 선택", options=c_list, index=c_idx, key=f"c_box_{v}")

with r0c2:
    project_df = df_raw[df_raw['고객사'] == selected_customer] if selected_customer != '전체' else df_raw
    p_list = ['전체'] + sorted(project_df['프로젝트명'].dropna().unique().tolist())
    p_idx = p_list.index(st.session_state.get('cur_project', '전체')) if st.session_state.get('cur_project') in p_list else 0
    selected_project = st.selectbox("📂 프로젝트명", options=p_list, index=p_idx, key=f"p_box_{v}")

r1c1, r1c2 = st.columns(2)
with r1c1:
    res = project_df[project_df['프로젝트명'] == selected_project] if selected_project != '전체' else project_df
    m_list = ['전체'] + sorted(res['강종명'].dropna().unique().tolist())
    m_idx = m_list.index(st.session_state.get('cur_mat', '전체')) if st.session_state.get('cur_mat') in m_list else 0
    selected_mat = st.selectbox("✨ 강종명 선택", options=m_list, index=m_idx, key=f"m_box_{v}")
with r1c2:
    thick_val = st.session_state.get('cur_thick')
    selected_thick = st.number_input("📏 두께 (T)", value=thick_val, placeholder="", format="%.2f", key=f"t_box_{v}")

r2c1, r2c2 = st.columns(2)
with r2c1: q_prod = st.number_input("생산 예상수량 (EA)", min_value=0, step=1000, key=f"q_p_{v}")
with r2c2: q_order = st.number_input("발주 수량 (EA)", min_value=0, step=1000, key=f"q_o_{v}")
loss = st.number_input("Loss율 (%)", value=3.0, step=0.5, key=f"loss_{v}")

st.divider()

# 7. 상세 사양 선택
filtered = res[res['강종명'] == selected_mat] if selected_mat != "전체" else res
if selected_thick is not None:
    filtered = filtered[filtered['두께'] == selected_thick]

calc_ready = filtered.dropna(subset=['단중']).copy() if '단중' in filtered.columns else pd.DataFrame()

if not calc_ready.empty:
    calc_ready['label'] = calc_ready.apply(
        lambda x: f"[{x.get('프로젝트명','-')}] {x['강종명']} ({x.get('두께','-')} * {x.get('폭','-')}) / 단중: {x['단중']:.4f}", axis=1
    )
    s_options = ["선택하세요"] + calc_ready['label'].tolist()
    st.selectbox("🎯 상세 사양 선택 (단중 기입 항목만 표시)", options=s_options, key=f"spec_select_{v}", on_change=on_spec_change)
    
    b1, b2 = st.columns(2)
    with b1: apply_clicked = st.button("🚀 계산 결과 적용", type="primary", use_container_width=True)
    with b2: 
        if st.button("🔄 입력 초기화", use_container_width=True):
            reset_all()

    # 결과창 출력
    if apply_clicked and st.session_state[f"spec_select_{v}"] != "선택하세요":
        row = calc_ready[calc_ready['label'] == st.session_state[f"spec_select_{v}"]].iloc[0]
        u_w = float(row['단중'])
        
        res_md = ""
        if q_prod > 0:
            p_kg = (u_w * q_prod) * (1 + (loss / 100))
            res_md += f"🏭 **생산 예상수량 결과:** \n #### :green[`{p_kg:,.1f} kg`] ({p_kg/1000:,.2f} ton) / {q_prod:,} EA  \n\n"
        if q_order > 0:
            o_kg = (u_w * q_order) * (1 + (loss / 100))
            # [요청 사항 반영] 문구 수정
            res_md += f"📦 **발주 수량 결과:** \n #### 구매필요량 : :green[`{o_kg:,.1f} kg`] ({o_kg/1000:,.2f} ton) / 발주량 : `{q_order:,} EA`"
        
        if q_prod == 0 and q_order == 0: res_md = "⚠️ 수량을 입력해주세요."
        st.success(res_md)

        st.info(f"""
### 📋 상세 정보
- **고객사:** {row['고객사']}
- **프로젝트:** {row.get('프로젝트명','-')}
- **규격:** {row['강종명']} ({row['두께']} * {row['폭']})
- **단중:** `{u_w:.4f} kg`
- **※ 적용 요약 (LOSS {loss}%)**
""")
else:
    st.warning("조건에 맞는 데이터가 없습니다. [입력 초기화] 후 다시 시도해 주세요.")

if st.sidebar.button("🚪 로그아웃"):
    st.session_state.auth_success = False
    st.rerun()
