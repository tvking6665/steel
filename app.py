import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="전우정밀 원소재 시스템", layout="centered")

# 2. 제목
st.markdown("### 🏢 전우정밀 (주) 원소재 정보 시스템")

# 3. 데이터 연결
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=600)

# 4. 고객사 선택
st.subheader("🤝 고객사 선택")
customer_list = ["전체"] + sorted(df['고객사'].unique().tolist())
selected_customer = st.selectbox("고객사를 선택하세요", customer_list, label_visibility="collapsed")

filtered_df = df if selected_customer == "전체" else df[df['고객사'] == selected_customer]

st.divider()

# 5. 핵심 입력 (강종/두께)
col1, col2 = st.columns(2)
with col1:
    mat_list = sorted(filtered_df['강종명'].unique().tolist())
    selected_mat = st.selectbox("✨ 강종명 선택", mat_list)
with col2:
    thickness = st.number_input("📏 두께 입력", value=None, placeholder="예: 1.3", format="%.2f")

st.divider()

# 6. 상세 사양 선택 (KeyError 방지 로직 추가)
st.subheader("🎯 상세 규격 선택")

spec_df = filtered_df[filtered_df['강종명'] == selected_mat]
if thickness is not None:
    spec_df = spec_df[spec_df['두께'] == thickness]

if not spec_df.empty:
    # '기타정보및사양' 열이 없으면 '비고'나 '강종명'으로 대체하도록 안전하게 처리
    def get_display_text(x):
        # 시트에서 사용할 수 있는 컬럼명을 순서대로 확인
        info = ""
        if '기타정보및사양' in x: info = x['기타정보및사양']
        elif '비고' in x: info = x['비고']
        
        return f"[{info}] 규격: {x['두께']}t x {x['폭']}w / 피치: {x['피치']}"

    spec_df['display_text'] = spec_df.apply(get_display_text, axis=1)
    
    selected_spec = st.selectbox(
        "상세 사양 선택",
        options=spec_df['display_text'].tolist(),
        label_visibility="collapsed"
    )
    
    if st.button("✅ 설정 내용 적용", type="primary", use_container_width=True):
        st.success("사양이 적용되었습니다.")
else:
    st.warning("일치하는 데이터가 없습니다. 강종과 두께를 다시 확인하세요.")

# 리스트 보기
with st.expander("📊 데이터 리스트 확인"):
    st.dataframe(filtered_df, use_container_width=True)
