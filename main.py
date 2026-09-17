import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("영화 데이터를 시간의 흐름에 따라 다양한 그래프로 살펴봅니다.")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "순위",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df


df = load_data()


# ==================================================
# 그래프 1
# ==================================================
st.divider()
st.header("📈 그래프 1. 영화별 일관객 변화")

st.write(
    "영화를 하나 선택하면 해당 영화의 날짜별 일관객 변화를 볼 수 있습니다."
)

movie_list = sorted(
    df["영화명"].dropna().unique()
)

selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
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
    hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
)

fig1.update_layout(
    hovermode="x unified",
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 작성하세요.",
    height=100,
    key="graph1_note"
)


# ==================================================
# 그래프 2
# ==================================================
st.divider()
st.header("📊 그래프 2. 일관객 합계 TOP 5 영화의 날짜별 변화")

st.write(
    "이 기간 동안 일관객 합계가 가장 큰 5편의 날짜별 일관객 변화를 비교합니다."
)

# 영화별 일관객 합계 TOP 5
top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

top5_df = df[
    df["영화명"].isin(top5_movies)
].copy()

top5_df = top5_df.sort_values(
    ["날짜", "영화명"]
)

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

fig2.update_traces(
    hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra>%{fullData.name}</extra>"
)

fig2.update_layout(
    hovermode="x unified",
    height=550,
    legend_title_text="영화"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 작성하세요.",
    height=100,
    key="graph2_note"
)


# ==================================================
# 그래프 3
# ==================================================
st.divider()
st.header("📊 그래프 3. 날짜별 10위권 일관객 합계")

st.write(
    "각 날짜의 박스오피스 10위권 영화들의 일관객을 모두 더해 "
    "하루 동안의 전체 관객 규모를 살펴봅니다."
)

# 날짜별 일관객 합계
daily_audience = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

# 일관객 합계가 가장 큰 날 3개
top3_days = (
    daily_audience
    .nlargest(3, "일관객")
    .sort_values("날짜")
)

fig3 = px.area(
    daily_audience,
    x="날짜",
    y="일관객",
    title="날짜별 10위권 일관객 합계",
    labels={
        "날짜": "날짜",
        "일관객": "10위권 일관객 합계"
    }
)

fig3.update_traces(
    hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,}명"
        "<extra></extra>"
)

# TOP 3 날짜 표시
for _, row in top3_days.iterrows():
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=(
            f"<b>{row['날짜'].strftime('%Y-%m-%d')}</b><br>"
            f"{row['일관객']:,}명"
        ),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50
    )

fig3.update_layout(
    hovermode="x unified",
    height=550
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 작성하세요.",
    height=100,
    key="graph3_note"
)


# ==================================================
# 그래프 4
# ==================================================
st.divider()
st.header("📊 그래프 4. 영화별 일관객 TOP 10")

st.write(
    "이 기간 동안 각 영화의 일관객을 모두 합산해 "
    "관객 수가 많은 영화 TOP 10을 비교합니다."
)

# --------------------------------------------------
# 영화별 총 일관객 + 10위권 등장 일수
# --------------------------------------------------
movie_summary = (
    df.groupby("영화명")
    .agg(
        총_일관객=("일관객", "sum"),
        등장일수=("날짜", "nunique")
    )
    .reset_index()
)

# 총 일관객 TOP 10
top10_movies = (
    movie_summary
    .sort_values(
        "총_일관객",
        ascending=False
    )
    .head(10)
    .sort_values(
        "총_일관객",
        ascending=True
    )
)

fig4 = px.bar(
    top10_movies,
    x="총_일관객",
    y="영화명",
    orientation="h",
    title="영화별 일관객 TOP 10",
    labels={
        "총_일관객": "이 기간 일관객 합계",
        "영화명": "영화"
    },
    text="총_일관객"
)

fig4.update_traces(
    texttemplate="%{text:,}명",
    textposition="outside",
    customdata=top10_movies[
        ["등장일수"]
    ].values,
    hovertemplate=
        "영화: %{y}<br>"
        "이 기간 일관객 합계: %{x:,}명<br>"
        "10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
)

fig4.update_layout(
    height=600
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 작성하세요.",
    height=100,
    key="graph4_note"
)


# ==================================================
# 그래프 5
# ==================================================
st.divider()
st.header("📊 그래프 5. 월 × 요일별 일관객 합계")

st.write(
    "월과 요일별로 10위권 영화의 일관객을 합산해 "
    "어떤 월·요일에 관객이 많았는지 한눈에 비교합니다."
)

# 날짜에서 월과 요일 추출
heatmap_df = df.copy()

heatmap_df["월"] = heatmap_df["날짜"].dt.month

weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

heatmap_df["요일"] = (
    heatmap_df["날짜"]
    .dt.dayofweek
    .map(dict(enumerate(weekday_order)))
)

# 월 × 요일별 일관객 합계
heatmap_data = (
    heatmap_df
    .groupby(["월", "요일"])["일관객"]
    .sum()
    .reset_index()
)

# 피벗
heatmap_pivot = heatmap_data.pivot(
    index="월",
    columns="요일",
    values="일관객"
)

# 월요일 → 일요일 순서
heatmap_pivot = heatmap_pivot.reindex(
    columns=weekday_order
)

# 1월 → 12월 순서
heatmap_pivot = heatmap_pivot.reindex(
    range(1, 13)
)

fig5 = px.imshow(
    heatmap_pivot,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    },
    x=weekday_order,
    y=[f"{month}월" for month in range(1, 13)],
    text_auto=",",
    aspect="auto",
    title="월 × 요일별 10위권 일관객 합계"
)

fig5.update_traces(
    hovertemplate=
        "%{y} %{x}<br>"
        "일관객 합계: %{z:,}명"
        "<extra></extra>"
)

fig5.update_layout(
    height=650,
    xaxis_title="요일",
    yaxis_title="월"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 작성하세요.",
    height=100,
    key="graph5_note"
)
