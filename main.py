import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("영화별 일관객 변화를 시간의 흐름에 따라 살펴보는 그래프입니다.")


# =========================================================
# 데이터 불러오기
# =========================================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8-sig"
    )

    # 날짜를 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


df = load_data()


# =========================================================
# 그래프 1
# =========================================================

st.header("📈 그래프 1. 영화별 일관객 변화")

st.write(
    "영화를 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다."
)

movie_list = sorted(
    df["영화명"].dropna().unique()
)

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list
)

movie_df = df[
    df["영화명"] == selected_movie
].copy()

movie_df = movie_df.sort_values("날짜")


fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig1.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y년 %m월 %d일}<br>"
        "일관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig1.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


st.subheader("📝 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프를 보고 알 수 있는 내용을 직접 작성하세요."
)


# =========================================================
# 그래프 2
# =========================================================

st.header("📈 그래프 2. 일관객 합계 TOP 5 영화")

st.write(
    "전체 기간 동안 일관객 합계가 가장 큰 5편의 날짜별 일관객 변화를 비교합니다."
)


# 영화별 전체 기간 일관객 합계
top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
    .tolist()
)


# TOP 5 영화 데이터만 선택
top5_df = df[
    df["영화명"].isin(top5_movies)
].copy()

top5_df = top5_df.sort_values(
    ["날짜", "영화명"]
)


# 선 그래프
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 TOP 5 영화의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)


# 마우스를 올렸을 때 날짜와 관객수 표시
fig2.update_traces(
    hovertemplate=(
        "영화: %{fullData.name}<br>"
        "날짜: %{x|%Y년 %m월 %d일}<br>"
        "일관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)


fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    height=600,
    legend_title="영화"
)


st.plotly_chart(
    fig2,
    use_container_width=True
)


st.subheader("📝 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프를 보고 알 수 있는 내용을 직접 작성하세요."
)


# =========================================================
# 그래프 3
# =========================================================

st.header("📊 그래프 3")

st.write(
    "앞으로 추가할 그래프 영역입니다."
)


# =========================================================
# 그래프 4
# =========================================================

st.header("📊 그래프 4")

st.write(
    "앞으로 추가할 그래프 영역입니다."
)
