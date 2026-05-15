import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정 및 스타일
st.set_page_config(page_title="전우정밀 원소재 시스템", layout="centered")

st.markdown("""
    <style>
    .main-title { font-size: 22px; font-weight: bold; color: #1E88E5; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 제목 및 로고
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try: 
        st.image("logo.png", width=50)
    except: 
        st.write("🏢")
with col_title:
    st.markdown('<p class="main-title">전우정밀 (주) 원소재 정보 시스템</p>', unsafe_allow_html=True)

# 3. 데이터 연결 (구글 시트)
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=600) 

# 4. 고객사 필터링
st.subheader("🤝 고객사 선택")
customer_list = ["전체"] + sorted(df['고객사'].unique().tolist())
selected_customer = st.selectbox("고객사를 선택하세요", customer_list, label_visibility="collapsed")

# 데이터 1차 필터링
filtered_df = df if selected_customer == "전체" else df[df['고객사'] == selected_customer]

st.divider()

# 5. 핵심 입력 섹션 (강종 드롭박스 + 두께 공란)
col1, col2 = st.columns(2)

with col1:
    # 강종명: 시트에 있는 목록을 드롭박스로 표시
    mat_list = sorted(filtered_df['강종명'].unique().tolist())
    selected_mat = st.selectbox("✨ 강종명 선택", mat_list)

with col2:
    # 두께: 기본값 없이 공란으로 표시 (placeholder 사용)
    thickness = st.number_input("📏 두께 입력", value=None, placeholder="예: 1.3", format="%.2f")

c3, c4 = st.columns(2)
with c3:
    est_qty = st.number_input("생산 예상수량 (EA)", min_value=0, value=0)
with c4:
    order_qty = st.number_input("발주 수량 (EA)", min_value=0, value=0)

loss_rate = st.number_input("Loss율 (%)", value=3.0, step=0.1)

st.divider()

# 6. 상세 규격 선택 (고객사명 생략 버전)
st.subheader("🎯 상세 규격 및 사양 선택")

# 상세 규격 필터링 (강종과 두께 기준)
spec_df = filtered_df[filtered_df['강종명'] == selected_mat]
if thickness is not None:
    spec_df = spec_df[spec_df['두께'] == thickness]

if not spec_df.empty:
    # [수정] 고객사명은 제외하고, 기타정보및사양을 앞쪽으로 배치하여 강조
    spec_df['display_text'] = spec_df.apply(
        lambda x: f"[{x['기타정보및사양']}] 규격: {x['두께']}t x {x['폭']}w / 피치: {x['피치']}", axis=1
    )
    
    selected_spec = st.selectbox(
        "사용하실 상세 사양을 선택하세요",
        options=spec_df['display_text'].tolist(),
        label_visibility="collapsed"
    )
    
    if st.button("✅ 설정 내용 적용", type="primary", use_container_width=True):
        st.success(f"[{selected_mat}] {thickness if thickness else ''} 사양이 적용되었습니다.")
else:
    st.warning("선택하신 강종 및 두께에 맞는 등록 데이터가 없습니다.")

# 7. 전체 리스트 확인용
with st.expander("📊 현재 필터링된 원소재 리스트 보기"):
    st.dataframe(filtered_df, use_container_width=True)
