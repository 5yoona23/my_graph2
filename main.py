import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write("영화의 장르별 분포와 여러 변수 사이의 관계를 살펴보는 그래프입니다.")


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일을 날짜 형식으로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 장르가 여러 개이면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("알 수 없음")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 열 변환
    numeric_columns = [
        "movieCd",
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()


# --------------------------------------------------
# 그래프 1
# --------------------------------------------------
st.divider()
st.header("🍩 그래프 1. 장르별 영화 편수")

# 장르별 영화 수 계산
genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화 편수"]

# Plotly 도넛 그래프
fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수",
)

# 마우스를 올렸을 때 편수와 비율 표시
fig1.update_traces(
    textinfo="label",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    legend_title_text="장르"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# --------------------------------------------------
# 그래프 1 설명 공간
# --------------------------------------------------
st.subheader("📝 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프로 알 수 있는 내용을 직접 작성하세요."
)


# --------------------------------------------------
# 그래프 2
# --------------------------------------------------
st.divider()
st.header("📊 그래프 2")
st.caption("앞으로 두 번째 그래프를 추가할 공간입니다.")

st.subheader("📝 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프로 알 수 있는 내용을 직접 작성하세요."
)


# --------------------------------------------------
# 그래프 3
# --------------------------------------------------
st.divider()
st.header("📊 그래프 3")
st.caption("앞으로 세 번째 그래프를 추가할 공간입니다.")

st.subheader("📝 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프로 알 수 있는 내용을 직접 작성하세요."
)


# --------------------------------------------------
# 그래프 4
# --------------------------------------------------
st.divider()
st.header("📊 그래프 4")
st.caption("앞으로 네 번째 그래프를 추가할 공간입니다.")

st.subheader("📝 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프로 알 수 있는 내용을 직접 작성하세요."
)
