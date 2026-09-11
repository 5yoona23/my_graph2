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
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜를 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
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
# 영화별 날짜에 따른 일관객 변화
# =========================================================

st.header("📈 그래프 1. 영화별 일관객 변화")

st.write("영화를 선택하면 해당 영화의 날짜별 일관객 변화를 확인할 수 있습니다.")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()

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
    },
    hover_data={
        "날짜": "|%Y년 %m월 %d일",
        "일관객": ":,.0f"
    }
)

fig1.update_traces(
    hovertemplate="날짜: %{x|%Y년 %m월 %d일}<br>일관객: %{y:,.0f}명<extra></extra>"
)

fig1.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    hovermode="x unified",
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# =========================================================
# 이 그래프로 알 수 있는 것
# =========================================================

st.subheader("📝 이 그래프로 알 수 있는 것")

st.info(
    "여기에 이 그래프를 보고 알 수 있는 내용을 직접 작성하세요."
)


# =========================================================
# 앞으로 추가할 그래프 구역
# =========================================================

st.divider()

st.header("📊 그래프 2")
st.caption("앞으로 추가할 그래프 영역")

# 여기에 두 번째 그래프를 추가


st.divider()

st.header("📊 그래프 3")
st.caption("앞으로 추가할 그래프 영역")

# 여기에 세 번째 그래프를 추가


st.divider()

st.header("📊 그래프 4")
st.caption("앞으로 추가할 그래프 영역")

# 여기에 네 번째 그래프를 추가
