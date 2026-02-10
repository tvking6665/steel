import streamlit as st
import pandas as pd

# 앱 설정: 모바일에서 크게 보이도록 세팅
st.set_page_config(page_title="현장용 강종 검색기", layout="centered")

# CSS를 이용해 표의 글자 크기를 키우고 가독성을 높임
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    div[data-testid="stExpander"] { border: none; }
    .stDataFrame { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 규격 조회 (캡처용)")

@st.cache_data
def load_data():
    try:
        # data.xlsx 파일을 읽어옵니다
        df = pd.read_excel("data.xlsx")
        # '두께(T)' 컬럼을 숫자형으로 변환합니다
        df['두께(T)'] = pd.to_numeric(df['두께(T)'], errors='coerce')
        return df
    except:
        return None

df = load_data()

if df is not None:
    # 입력창을 상단에 배치
    col1, col2 = st.columns(2)
    with col1:
        name_in = st.text_input("강종명", placeholder="SPFH590").strip()
    with col2:
        thick_in = st.text_input("두께(T)", placeholder="1.8").strip()

    # 검색 로직 수행
    res = df.copy()
    if name_in:
        res = res[res['소재명'].str.contains(name_in, case=False, na=False)]
    if thick_in:
        try:
            val = float(thick_in)
            res = res[res['두께(T)'] == val]
        except:
            st.error("숫자만!")

    st.divider()

    if not res.empty:
        # 결과 요약 표시
        st.subheader(f"✅ 검색 결과: {len(res)}건")
        
        # 표를 고정된 형태(Static Table)로 출력하여 스크린샷 찍기 좋게 만듦
        # 일반 dataframe보다 table 형태가 사진으로 찍었을 때 더 깔끔합니다.
        st.table(res)
        
        st.caption("위 화면을 스크린샷(캡처)해서 카톡으로 전송하세요!")
    else:
        st.info("조건에 맞는 소재가 없습니다.")
else:
    st.error("data.xlsx 파일을 찾을 수 없습니다.")
